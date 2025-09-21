from typing import List, Dict, Any, Optional, Tuple, Set
import asyncio
import aiohttp
import re
import json
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

from src.core.config import settings
from src.core.genai_client import GenAIClient
from src.models.models import Repository, GitHubAnalysisRequest
from src.db.crud import RepositoryCRUD
from src.utils.logging import setup_logger
import redis.asyncio as redis
import base64
import hashlib

logger = setup_logger(__name__)


class GitHubService:
    """Production-ready GitHub repository analysis service"""
    
    def __init__(self):
        self.github_token = settings.github_client_secret  # Use as PAT token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Guidora-AI-Career-Platform/1.0"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        self.genai_client = GenAIClient()
        self.repository_crud = RepositoryCRUD()
        self.redis_client = None
        self.session = None
        
        # Language detection patterns
        self.framework_patterns = {
            'react': ['react', 'jsx', '.jsx', 'react-dom'],
            'vue': ['vue', '.vue', 'vuejs'],
            'angular': ['angular', '@angular', 'ng-'],
            'express': ['express', 'express.js'],
            'django': ['django', 'requirements.txt', 'manage.py'],
            'flask': ['flask', 'app.py'],
            'spring': ['spring', '@SpringBootApplication'],
            'laravel': ['laravel', 'artisan', 'composer.json'],
            'rails': ['rails', 'gemfile', '.rb'],
            'nextjs': ['next.js', 'next', 'pages/'],
            'fastapi': ['fastapi', 'uvicorn'],
            'tensorflow': ['tensorflow', 'tf.', 'keras'],
            'pytorch': ['torch', 'pytorch', 'nn.'],
            'docker': ['dockerfile', 'docker-compose'],
            'kubernetes': ['k8s', 'kubectl', 'deployment.yaml']
        }
        
    async def initialize(self):
        """Initialize HTTP session and Redis connection"""
        try:
            # Initialize HTTP session
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
            
            # Initialize Redis for caching
            if settings.cache_llm_responses:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    password=settings.redis_password,
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("GitHub service Redis connection established")
            
            logger.info("GitHubService initialized successfully")
            
        except Exception as e:
            logger.warning(f"GitHubService initialization warning: {e}")

    async def analyze_repositories(self, request: GitHubAnalysisRequest) -> List[Repository]:
        """Analyze multiple GitHub repositories"""
        try:
            logger.info(f"Analyzing {len(request.repository_urls)} repositories for user {request.user_id}")
            
            # Process repositories concurrently
            analysis_tasks = []
            for repo_url in request.repository_urls:
                task = self._analyze_single_repository(
                    request.user_id,
                    repo_url,
                    request.analyze_code_quality,
                    request.analyze_activity
                )
                analysis_tasks.append(task)
            
            # Execute analyses concurrently with semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent GitHub API calls
            async def bounded_analysis(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(
                *[bounded_analysis(task) for task in analysis_tasks],
                return_exceptions=True
            )
            
            # Process results and filter out exceptions
            repositories = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing repository {request.repository_urls[i]}: {result}")
                elif result:
                    repositories.append(result)
            
            logger.info(f"Successfully analyzed {len(repositories)} repositories for user {request.user_id}")
            return repositories
            
        except Exception as e:
            logger.error(f"Error in analyze_repositories: {e}")
            raise

    async def _analyze_single_repository(
        self,
        user_id: str,
        repo_url: str,
        analyze_code_quality: bool = True,
        analyze_activity: bool = True
    ) -> Optional[Repository]:
        """Analyze a single GitHub repository"""
        try:
            logger.info(f"Analyzing repository: {repo_url}")
            
            # Parse repository URL
            owner, repo_name = self._parse_repo_url(repo_url)
            if not owner or not repo_name:
                logger.error(f"Invalid repository URL: {repo_url}")
                return None
            
            # Check cache first
            cached_repo = await self._get_cached_analysis(repo_url)
            if cached_repo:
                logger.info(f"Using cached analysis for {repo_url}")
                cached_repo.user_id = user_id  # Update user_id
                await self.repository_crud.save_repository(cached_repo)
                return cached_repo
            
            # Gather repository data
            repo_data = await self._gather_repository_data(owner, repo_name, analyze_activity)
            if not repo_data:
                return None
            
            # Analyze code quality if requested
            code_quality_metrics = {}
            if analyze_code_quality:
                code_quality_metrics = await self._analyze_code_quality(owner, repo_name, repo_data)
            
            # Detect technologies and frameworks
            technologies, dependencies = await self._detect_technologies(owner, repo_name, repo_data)
            
            # Create Repository model
            repository = Repository(
                user_id=user_id,
                repo_id=f"{owner}/{repo_name}",
                repo_name=repo_name,
                repo_url=repo_url,
                owner=owner,
                description=repo_data.get('description'),
                primary_language=repo_data.get('language', 'Unknown'),
                languages=repo_data.get('languages', {}),
                total_commits=repo_data.get('total_commits', 0),
                contributors=repo_data.get('contributors_count', 0),
                stars=repo_data.get('stargazers_count', 0),
                forks=repo_data.get('forks_count', 0),
                code_quality_score=code_quality_metrics.get('quality_score'),
                complexity_score=code_quality_metrics.get('complexity_score'),
                documentation_score=code_quality_metrics.get('documentation_score'),
                technologies=list(technologies),
                dependencies=dependencies,
                last_commit_date=repo_data.get('last_commit_date'),
                commit_frequency=repo_data.get('commit_frequency'),
                active_months=repo_data.get('active_months', 0)
            )
            
            # Save to database
            await self.repository_crud.save_repository(repository)
            
            # Cache the analysis
            await self._cache_analysis(repo_url, repository)
            
            logger.info(f"Successfully analyzed repository {owner}/{repo_name}")
            return repository
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_url}: {e}")
            return None

    async def _gather_repository_data(self, owner: str, repo_name: str, analyze_activity: bool) -> Optional[Dict[str, Any]]:
        """Gather basic repository data from GitHub API"""
        try:
            # Get repository info
            repo_url = f"{self.base_url}/repos/{owner}/{repo_name}"
            async with self.session.get(repo_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch repository info: {response.status}")
                    return None
                
                repo_info = await response.json()
            
            # Get languages
            languages_url = f"{self.base_url}/repos/{owner}/{repo_name}/languages"
            languages = {}
            try:
                async with self.session.get(languages_url) as response:
                    if response.status == 200:
                        languages_raw = await response.json()
                        total_bytes = sum(languages_raw.values())
                        if total_bytes > 0:
                            languages = {
                                lang: round((bytes_count / total_bytes) * 100, 2)
                                for lang, bytes_count in languages_raw.items()
                            }
            except Exception as e:
                logger.warning(f"Could not fetch languages for {owner}/{repo_name}: {e}")
            
            repo_data = {
                'description': repo_info.get('description'),
                'language': repo_info.get('language'),
                'languages': languages,
                'stargazers_count': repo_info.get('stargazers_count', 0),
                'forks_count': repo_info.get('forks_count', 0),
                'created_at': repo_info.get('created_at'),
                'updated_at': repo_info.get('updated_at'),
                'pushed_at': repo_info.get('pushed_at')
            }
            
            # Get commit activity if requested
            if analyze_activity:
                activity_data = await self._analyze_commit_activity(owner, repo_name)
                repo_data.update(activity_data)
            
            # Get contributors count
            contributors_count = await self._get_contributors_count(owner, repo_name)
            repo_data['contributors_count'] = contributors_count
            
            return repo_data
            
        except Exception as e:
            logger.error(f"Error gathering repository data: {e}")
            return None

    async def _analyze_commit_activity(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """Analyze commit activity patterns"""
        try:
            # Get commit activity (weekly stats)
            activity_url = f"{self.base_url}/repos/{owner}/{repo_name}/stats/participation"
            commit_frequency = 0.0
            active_months = 0
            last_commit_date = None
            total_commits = 0
            
            try:
                async with self.session.get(activity_url) as response:
                    if response.status == 200:
                        activity_data = await response.json()
                        if activity_data and 'all' in activity_data:
                            weekly_commits = activity_data['all']
                            total_commits = sum(weekly_commits)
                            
                            # Calculate monthly average
                            weeks_with_commits = len([w for w in weekly_commits if w > 0])
                            if weeks_with_commits > 0:
                                commit_frequency = total_commits / (weeks_with_commits / 4.33)  # weeks to months
                                active_months = max(1, weeks_with_commits // 4)
            except Exception as e:
                logger.warning(f"Could not fetch activity for {owner}/{repo_name}: {e}")
            
            # Get latest commit date
            try:
                commits_url = f"{self.base_url}/repos/{owner}/{repo_name}/commits"
                async with self.session.get(commits_url, params={'per_page': 1}) as response:
                    if response.status == 200:
                        commits = await response.json()
                        if commits:
                            commit_date_str = commits[0]['commit']['author']['date']
                            last_commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Could not fetch latest commit for {owner}/{repo_name}: {e}")
            
            return {
                'total_commits': total_commits,
                'commit_frequency': round(commit_frequency, 2),
                'active_months': active_months,
                'last_commit_date': last_commit_date
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing commit activity: {e}")
            return {
                'total_commits': 0,
                'commit_frequency': 0.0,
                'active_months': 0,
                'last_commit_date': None
            }

    async def _get_contributors_count(self, owner: str, repo_name: str) -> int:
        """Get number of contributors"""
        try:
            contributors_url = f"{self.base_url}/repos/{owner}/{repo_name}/contributors"
            async with self.session.get(contributors_url, params={'per_page': 1}) as response:
                if response.status == 200:
                    # GitHub returns the Link header with pagination info
                    link_header = response.headers.get('Link', '')
                    if 'rel="last"' in link_header:
                        # Parse the last page number from Link header
                        last_page_match = re.search(r'page=(\d+)>; rel="last"', link_header)
                        if last_page_match:
                            return int(last_page_match.group(1))
                    
                    # If no pagination, count the actual contributors
                    contributors = await response.json()
                    return len(contributors)
                
                return 0
        except Exception as e:
            logger.warning(f"Could not fetch contributors count: {e}")
            return 0

    async def _detect_technologies(self, owner: str, repo_name: str, repo_data: Dict) -> Tuple[Set[str], List[str]]:
        """Detect technologies and frameworks used"""
        try:
            technologies = set()
            dependencies = []
            
            # Add primary language
            primary_lang = repo_data.get('language')
            if primary_lang:
                technologies.add(primary_lang.lower())
            
            # Add languages
            for lang in repo_data.get('languages', {}).keys():
                technologies.add(lang.lower())
            
            # Get repository contents to detect frameworks
            contents_url = f"{self.base_url}/repos/{owner}/{repo_name}/contents"
            try:
                async with self.session.get(contents_url) as response:
                    if response.status == 200:
                        contents = await response.json()
                        
                        # Check for specific files that indicate frameworks/technologies
                        filenames = [item['name'].lower() for item in contents if item['type'] == 'file']
                        
                        # Detect frameworks based on files
                        for framework, patterns in self.framework_patterns.items():
                            for pattern in patterns:
                                if any(pattern in filename for filename in filenames):
                                    technologies.add(framework)
                                    break
                        
                        # Get dependencies from specific files
                        dependency_files = {
                            'package.json': 'node',
                            'requirements.txt': 'python',
                            'composer.json': 'php',
                            'Gemfile': 'ruby',
                            'pom.xml': 'java',
                            'build.gradle': 'java',
                            'Cargo.toml': 'rust',
                            'go.mod': 'go'
                        }
                        
                        for filename in filenames:
                            if filename in dependency_files:
                                deps = await self._extract_dependencies(owner, repo_name, filename, dependency_files[filename])
                                dependencies.extend(deps)
                        
            except Exception as e:
                logger.warning(f"Could not analyze repository contents: {e}")
            
            return technologies, dependencies[:20]  # Limit to top 20 dependencies
            
        except Exception as e:
            logger.warning(f"Error detecting technologies: {e}")
            return set(), []

    async def _extract_dependencies(self, owner: str, repo_name: str, filename: str, lang_type: str) -> List[str]:
        """Extract dependencies from specific files"""
        try:
            file_url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{filename}"
            async with self.session.get(file_url) as response:
                if response.status == 200:
                    file_data = await response.json()
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    
                    dependencies = []
                    
                    if filename == 'package.json' and lang_type == 'node':
                        try:
                            package_data = json.loads(content)
                            deps = package_data.get('dependencies', {})
                            dev_deps = package_data.get('devDependencies', {})
                            dependencies = list(deps.keys()) + list(dev_deps.keys())
                        except json.JSONDecodeError:
                            pass
                    
                    elif filename == 'requirements.txt' and lang_type == 'python':
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (before ==, >=, etc.)
                                package = re.split(r'[=<>!]', line)[0].strip()
                                if package:
                                    dependencies.append(package)
                    
                    elif filename == 'composer.json' and lang_type == 'php':
                        try:
                            composer_data = json.loads(content)
                            deps = composer_data.get('require', {})
                            dev_deps = composer_data.get('require-dev', {})
                            dependencies = list(deps.keys()) + list(dev_deps.keys())
                        except json.JSONDecodeError:
                            pass
                    
                    return dependencies[:10]  # Top 10 dependencies per file
                
        except Exception as e:
            logger.warning(f"Could not extract dependencies from {filename}: {e}")
        
        return []

    async def _analyze_code_quality(self, owner: str, repo_name: str, repo_data: Dict) -> Dict[str, float]:
        """Analyze code quality metrics using AI"""
        try:
            # Get repository structure and sample files
            structure_info = await self._get_repository_structure(owner, repo_name)
            
            # Create prompt for AI analysis
            prompt = f"""
            Analyze the code quality of this GitHub repository and provide scores (0-10):

            Repository: {owner}/{repo_name}
            Description: {repo_data.get('description', 'No description')}
            Primary Language: {repo_data.get('language', 'Unknown')}
            Stars: {repo_data.get('stargazers_count', 0)}
            Contributors: {repo_data.get('contributors_count', 0)}

            Repository Structure:
            {structure_info}

            Provide scores for:
            1. Code Quality (0-10): Overall code organization, naming conventions, structure
            2. Complexity (0-10): Code complexity and maintainability (10 = low complexity, good)
            3. Documentation (0-10): README, comments, documentation quality

            Respond with only a JSON object:
            {{"quality_score": X.X, "complexity_score": X.X, "documentation_score": X.X}}
            """
            
            # Get AI analysis (with fallback to basic metrics)
            try:
                ai_response = await self.genai_client.generate_text(prompt)
                
                # Parse AI response
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    quality_data = json.loads(ai_response[json_start:json_end])
                    return {
                        'quality_score': float(quality_data.get('quality_score', 5.0)),
                        'complexity_score': float(quality_data.get('complexity_score', 5.0)),
                        'documentation_score': float(quality_data.get('documentation_score', 5.0))
                    }
                
            except Exception as ai_e:
                logger.warning(f"AI code quality analysis failed: {ai_e}")
            
            # Fallback to basic heuristics
            return self._calculate_basic_quality_metrics(repo_data)
            
        except Exception as e:
            logger.warning(f"Error analyzing code quality: {e}")
            return {'quality_score': 5.0, 'complexity_score': 5.0, 'documentation_score': 5.0}

    async def _get_repository_structure(self, owner: str, repo_name: str) -> str:
        """Get repository structure for AI analysis"""
        try:
            contents_url = f"{self.base_url}/repos/{owner}/{repo_name}/contents"
            async with self.session.get(contents_url) as response:
                if response.status == 200:
                    contents = await response.json()
                    
                    structure = []
                    for item in contents[:20]:  # Limit to first 20 items
                        if item['type'] == 'file':
                            structure.append(f"📄 {item['name']}")
                        elif item['type'] == 'dir':
                            structure.append(f"📁 {item['name']}/")
                    
                    return '\n'.join(structure)
                
        except Exception as e:
            logger.warning(f"Could not get repository structure: {e}")
        
        return "Structure unavailable"

    def _calculate_basic_quality_metrics(self, repo_data: Dict) -> Dict[str, float]:
        """Calculate basic quality metrics as fallback"""
        try:
            # Basic scoring based on repository characteristics
            stars = repo_data.get('stargazers_count', 0)
            contributors = repo_data.get('contributors_count', 0)
            has_description = bool(repo_data.get('description'))
            
            # Quality score based on stars and contributors
            quality_score = min(10, (stars / 100) + (contributors * 0.5) + (3 if has_description else 0))
            
            # Complexity score (assume average for unknown repos)
            complexity_score = 6.0
            
            # Documentation score based on description
            documentation_score = 7.0 if has_description else 4.0
            
            return {
                'quality_score': round(quality_score, 1),
                'complexity_score': complexity_score,
                'documentation_score': documentation_score
            }
            
        except Exception as e:
            logger.warning(f"Error calculating basic quality metrics: {e}")
            return {'quality_score': 5.0, 'complexity_score': 5.0, 'documentation_score': 5.0}

    def _parse_repo_url(self, repo_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse GitHub repository URL"""
        try:
            # Handle different URL formats
            if repo_url.startswith('https://github.com/'):
                path = repo_url.replace('https://github.com/', '')
            elif repo_url.startswith('https://www.github.com/'):
                path = repo_url.replace('https://www.github.com/', '')
            elif repo_url.startswith('github.com/'):
                path = repo_url.replace('github.com/', '')
            else:
                return None, None
            
            # Remove .git suffix if present
            path = path.rstrip('.git')
            
            # Split owner and repo name
            parts = path.split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing repository URL {repo_url}: {e}")
            return None, None

    async def _get_cached_analysis(self, repo_url: str) -> Optional[Repository]:
        """Get cached repository analysis"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"github_analysis:{hashlib.md5(repo_url.encode()).hexdigest()}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                repo_dict = json.loads(cached_data)
                return Repository(**repo_dict)
            
        except Exception as e:
            logger.warning(f"Error retrieving cached analysis: {e}")
        
        return None

    async def _cache_analysis(self, repo_url: str, repository: Repository):
        """Cache repository analysis"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"github_analysis:{hashlib.md5(repo_url.encode()).hexdigest()}"
            cache_data = repository.json()
            
            # Cache for 24 hours
            await self.redis_client.setex(cache_key, 86400, cache_data)
            logger.info(f"GitHub analysis cached for {repo_url}")
            
        except Exception as e:
            logger.warning(f"Error caching analysis: {e}")

    async def get_user_repositories(self, user_id: str) -> List[Repository]:
        """Get all analyzed repositories for a user"""
        return await self.repository_crud.get_user_repositories(user_id)

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            if self.redis_client:
                await self.redis_client.close()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


# Global instance
github_service = GitHubService()


async def initialize_github_service():
    """Initialize the GitHub service"""
    await github_service.initialize()
    logger.info("GitHubService initialized")


# Export
__all__ = ['GitHubService', 'github_service', 'initialize_github_service']
