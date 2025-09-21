from typing import List, Dict, Any, Optional, Set, Tuple
import asyncio
import json
import re
import random
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, urljoin
import hashlib

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

from src.core.config import settings
from src.models.models import LinkedInProfile, LinkedInScrapingRequest, LinkedInSectionType
from src.db.crud import LinkedInCRUD
from src.utils.logging import setup_logger
import redis.asyncio as redis

logger = setup_logger(__name__)


class LinkedInService:
    """Production-ready LinkedIn profile scraping service using Playwright"""
    
    def __init__(self):
        self.linkedin_crud = LinkedInCRUD()
        self.redis_client = None
        self.browser = None
        self.context = None
        
        # Rate limiting tracking
        self.request_times = []
        self.max_requests_per_hour = settings.linkedin_rate_limit_per_hour
        
        # Scraping configuration
        self.base_delay = settings.linkedin_delay_min_seconds
        self.max_delay = settings.linkedin_delay_max_seconds
        self.max_retries = settings.linkedin_max_retries
        self.timeout = settings.linkedin_timeout_seconds * 1000  # Convert to milliseconds
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Proxy configuration
        self.proxy_list = settings.get_linkedin_proxy_list() if hasattr(settings, 'get_linkedin_proxy_list') else []
        self.current_proxy_index = 0
        
    async def initialize(self):
        """Initialize browser, context, and Redis connection"""
        try:
            # Initialize Redis for caching and rate limiting
            if settings.cache_llm_responses:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    password=settings.redis_password,
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("LinkedIn service Redis connection established")
            
            # Initialize Playwright browser
            await self._initialize_browser()
            
            logger.info("LinkedInService initialized successfully")
            
        except Exception as e:
            logger.error(f"LinkedInService initialization failed: {e}")
            raise

    async def _initialize_browser(self):
        """Initialize Playwright browser and context"""
        try:
            self.playwright = await async_playwright().start()
            
            # Browser launch options
            launch_options = {
                'headless': settings.linkedin_headless_mode,
                'args': [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-web-security',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--no-first-run',
                    '--no-default-browser-check'
                ]
            }
            
            # Add executable path if specified
            if settings.browser_executable_path:
                launch_options['executable_path'] = settings.browser_executable_path
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create context with anti-detection settings
            await self._create_browser_context()
            
            logger.info("Playwright browser initialized")
            
        except Exception as e:
            logger.error(f"Browser initialization failed: {e}")
            raise

    async def _create_browser_context(self):
        """Create browser context with anti-detection measures"""
        try:
            context_options = {
                'viewport': {
                    'width': settings.browser_window_width,
                    'height': settings.browser_window_height
                },
                'user_agent': random.choice(self.user_agents),
                'java_script_enabled': True,
                'accept_downloads': False,
                'ignore_https_errors': True,
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
            
            # Add proxy if available
            if settings.linkedin_proxy_enabled and self.proxy_list:
                proxy_url = self._get_next_proxy()
                if proxy_url:
                    context_options['proxy'] = {'server': proxy_url}
            
            self.context = await self.browser.new_context(**context_options)
            
            # Add stealth scripts
            await self.context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state:'denied' }) :
                        originalQuery(parameters)
                );
            """)
            
        except Exception as e:
            logger.error(f"Context creation failed: {e}")
            raise

    async def scrape_profile(self, request: LinkedInScrapingRequest) -> LinkedInProfile:
        """Scrape LinkedIn profile"""
        try:
            logger.info(f"Starting LinkedIn scraping for user {request.user_id}: {request.profile_url}")
            
            # Check rate limits
            if not await self._check_rate_limit():
                raise Exception("Rate limit exceeded. Please try again later.")
            
            # Validate URL
            if not self._is_valid_linkedin_url(request.profile_url):
                raise ValueError("Invalid LinkedIn profile URL")
            
            # Check cache first
            cached_profile = await self._get_cached_profile(request.profile_url)
            if cached_profile and self._is_cache_fresh(cached_profile):
                logger.info(f"Using cached LinkedIn profile for {request.profile_url}")
                cached_profile.user_id = request.user_id
                await self.linkedin_crud.save_linkedin_profile(cached_profile)
                return cached_profile
            
            # Create new page for scraping
            page = await self.context.new_page()
            
            try:
                # Perform scraping
                profile_data = await self._scrape_profile_data(page, request)
                
                # Create LinkedInProfile model
                linkedin_profile = LinkedInProfile(
                    user_id=request.user_id,
                    profile_url=request.profile_url,
                    **profile_data
                )
                
                # Save to database
                await self.linkedin_crud.save_linkedin_profile(linkedin_profile)
                
                # Cache the profile
                await self._cache_profile(request.profile_url, linkedin_profile)
                
                logger.info(f"Successfully scraped LinkedIn profile for user {request.user_id}")
                return linkedin_profile
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile: {e}")
            raise

    async def _scrape_profile_data(self, page: Page, request: LinkedInScrapingRequest) -> Dict[str, Any]:
        """Scrape profile data from LinkedIn page"""
        profile_data = {
            'scraping_success': False,
            'scraping_errors': [],
            'sections_scraped': []
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                # Navigate to profile
                await self._navigate_with_retry(page, request.profile_url)
                
                # Wait for page load and add random delay
                await self._smart_wait(page)
                await self._random_delay()
                
                # Scrape different sections based on request
                for section_type in request.sections_to_scrape:
                    try:
                        section_data = await self._scrape_section(page, section_type)
                        if section_data:
                            profile_data.update(section_data)
                            profile_data['sections_scraped'].append(section_type)
                    except Exception as section_error:
                        logger.warning(f"Failed to scrape {section_type}: {section_error}")
                        profile_data['scraping_errors'].append(f"{section_type}: {str(section_error)}")
                
                profile_data['scraping_success'] = len(profile_data['sections_scraped']) > 0
                break
                
            except PlaywrightTimeoutError:
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.warning(f"Timeout on attempt {retry_count}, retrying...")
                    await self._random_delay(multiplier=2)
                    
                    # Rotate proxy if enabled
                    if settings.linkedin_proxy_rotation and self.proxy_list:
                        await self._rotate_proxy()
                else:
                    profile_data['scraping_errors'].append("Maximum retries exceeded due to timeouts")
                    break
                    
            except Exception as e:
                profile_data['scraping_errors'].append(str(e))
                break
        
        return profile_data

    async def _navigate_with_retry(self, page: Page, url: str):
        """Navigate to URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                await page.goto(url, wait_until='networkidle', timeout=self.timeout)
                return
            except PlaywrightTimeoutError:
                if attempt < self.max_retries - 1:
                    await self._random_delay(multiplier=2)
                    continue
                raise
            except Exception as e:
                if attempt < self.max_retries - 1 and "net::ERR_" in str(e):
                    await self._random_delay(multiplier=2)
                    continue
                raise

    async def _smart_wait(self, page: Page):
        """Smart waiting for page elements"""
        try:
            # Wait for main profile elements
            selectors_to_wait = [
                'h1',  # Name
                '[data-generated-suggestion-target]',  # Profile section
                '.pv-text-details__left-panel',  # Profile details
                '.pv-top-card'  # Top card
            ]
            
            for selector in selectors_to_wait:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    break
                except:
                    continue
            
            # Additional wait for dynamic content
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            logger.warning(f"Smart wait failed: {e}")

    async def _scrape_section(self, page: Page, section_type: LinkedInSectionType) -> Optional[Dict[str, Any]]:
        """Scrape specific profile section"""
        try:
            if section_type == LinkedInSectionType.EXPERIENCE:
                return await self._scrape_experience(page)
            elif section_type == LinkedInSectionType.EDUCATION:
                return await self._scrape_education(page)
            elif section_type == LinkedInSectionType.SKILLS:
                return await self._scrape_skills(page)
            elif section_type == LinkedInSectionType.CERTIFICATIONS:
                return await self._scrape_certifications(page)
            elif section_type == LinkedInSectionType.PROJECTS:
                return await self._scrape_projects(page)
            else:
                # Basic profile info (always scraped)
                return await self._scrape_basic_info(page)
                
        except Exception as e:
            logger.error(f"Error scraping {section_type}: {e}")
            return None

    async def _scrape_basic_info(self, page: Page) -> Dict[str, Any]:
        """Scrape basic profile information"""
        info = {}
        
        try:
            # Name
            name_selectors = [
                'h1.text-heading-xlarge',
                'h1[data-test-id="hero-name"]',
                '.pv-text-details__left-panel h1',
                'h1.break-words'
            ]
            info['full_name'] = await self._get_text_from_selectors(page, name_selectors)
            
            # Headline
            headline_selectors = [
                '.text-body-medium.break-words',
                '.pv-text-details__left-panel .text-body-medium',
                '[data-generated-suggestion-target]'
            ]
            info['headline'] = await self._get_text_from_selectors(page, headline_selectors)
            
            # Location
            location_selectors = [
                '.text-body-small.inline.t-black--light.break-words',
                '.pv-text-details__left-panel .text-body-small',
                '.pv-top-card--list-bullet .pv-top-card--list-bullet'
            ]
            info['location'] = await self._get_text_from_selectors(page, location_selectors)
            
            # About section
            try:
                about_button = page.locator('button:has-text("Show all")')
                if await about_button.is_visible():
                    await about_button.click()
                    await page.wait_for_timeout(1000)
                
                about_selectors = [
                    '.pv-about__summary-text',
                    '.inline-show-more-text',
                    '[data-field="summary_expanded"]'
                ]
                info['summary'] = await self._get_text_from_selectors(page, about_selectors)
                
            except Exception:
                info['summary'] = None
            
        except Exception as e:
            logger.warning(f"Error scraping basic info: {e}")
        
        return info

    async def _scrape_experience(self, page: Page) -> Dict[str, Any]:
        """Scrape work experience"""
        experience_data = {'experience': [], 'current_position': None, 'current_company': None}
        
        try:
            # Try to find experience section
            experience_section = page.locator('#experience').first
            if await experience_section.is_visible():
                # Get all experience items
                experience_items = page.locator('[data-field="experience"] .pvs-list__item--line-separated')
                
                count = await experience_items.count()
                for i in range(min(count, 10)):  # Limit to 10 most recent
                    try:
                        item = experience_items.nth(i)
                        
                        # Extract job title
                        title = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        
                        # Extract company
                        company = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        
                        # Extract duration
                        duration = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        
                        # Extract location
                        location = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').nth(1).text_content()
                        
                        experience_entry = {
                            'title': title.strip() if title else '',
                            'company': company.strip() if company else '',
                            'duration': duration.strip() if duration else '',
                            'location': location.strip() if location else ''
                        }
                        
                        experience_data['experience'].append(experience_entry)
                        
                        # Set current position (first in list)
                        if i == 0 and title and company:
                            experience_data['current_position'] = title.strip()
                            experience_data['current_company'] = company.strip()
                        
                    except Exception as item_error:
                        logger.warning(f"Error extracting experience item {i}: {item_error}")
                        continue
            
        except Exception as e:
            logger.warning(f"Error scraping experience: {e}")
        
        return experience_data

    async def _scrape_education(self, page: Page) -> Dict[str, Any]:
        """Scrape education information"""
        education_data = {'education': []}
        
        try:
            education_section = page.locator('#education').first
            if await education_section.is_visible():
                education_items = page.locator('[data-field="education"] .pvs-list__item--line-separated')
                
                count = await education_items.count()
                for i in range(min(count, 5)):  # Limit to 5 entries
                    try:
                        item = education_items.nth(i)
                        
                        school = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        degree = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        duration = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        
                        education_entry = {
                            'school': school.strip() if school else '',
                            'degree': degree.strip() if degree else '',
                            'duration': duration.strip() if duration else ''
                        }
                        
                        education_data['education'].append(education_entry)
                        
                    except Exception as item_error:
                        logger.warning(f"Error extracting education item {i}: {item_error}")
                        continue
                        
        except Exception as e:
            logger.warning(f"Error scraping education: {e}")
        
        return education_data

    async def _scrape_skills(self, page: Page) -> Dict[str, Any]:
        """Scrape skills and endorsements"""
        skills_data = {'skills': [], 'top_skills': []}
        
        try:
            # Try to expand skills section
            skills_button = page.locator('button:has-text("Show all"):has-text("skills")')
            if await skills_button.is_visible():
                await skills_button.click()
                await page.wait_for_timeout(2000)
            
            skills_items = page.locator('[data-field="skill_details"] .pvs-list__item--line-separated')
            
            count = await skills_items.count()
            for i in range(min(count, 20)):  # Limit to 20 skills
                try:
                    item = skills_items.nth(i)
                    
                    skill_name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                    
                    # Try to get endorsement count
                    endorsement_element = item.locator('.t-14.t-black--light')
                    endorsements = 0
                    if await endorsement_element.is_visible():
                        endorsement_text = await endorsement_element.text_content()
                        endorsement_match = re.search(r'(\d+)', endorsement_text or '')
                        if endorsement_match:
                            endorsements = int(endorsement_match.group(1))
                    
                    skill_entry = {
                        'skill': skill_name.strip() if skill_name else '',
                        'endorsements': endorsements
                    }
                    
                    skills_data['skills'].append(skill_entry)
                    
                    # Add to top skills if highly endorsed
                    if endorsements > 5:
                        skills_data['top_skills'].append(skill_name.strip())
                        
                except Exception as item_error:
                    logger.warning(f"Error extracting skill item {i}: {item_error}")
                    continue
            
            # Sort top skills by endorsements and take top 10
            skills_data['top_skills'] = skills_data['top_skills'][:10]
            
        except Exception as e:
            logger.warning(f"Error scraping skills: {e}")
        
        return skills_data

    async def _scrape_certifications(self, page: Page) -> Dict[str, Any]:
        """Scrape certifications"""
        cert_data = {'certifications': []}
        
        try:
            cert_section = page.locator('#licenses_and_certifications').first
            if await cert_section.is_visible():
                cert_items = page.locator('[data-field="certificationDetails"] .pvs-list__item--line-separated')
                
                count = await cert_items.count()
                for i in range(min(count, 10)):
                    try:
                        item = cert_items.nth(i)
                        
                        cert_name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        issuer = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        date = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        
                        cert_entry = {
                            'name': cert_name.strip() if cert_name else '',
                            'issuer': issuer.strip() if issuer else '',
                            'date': date.strip() if date else ''
                        }
                        
                        cert_data['certifications'].append(cert_entry)
                        
                    except Exception as item_error:
                        logger.warning(f"Error extracting certification item {i}: {item_error}")
                        continue
                        
        except Exception as e:
            logger.warning(f"Error scraping certifications: {e}")
        
        return cert_data

    async def _scrape_projects(self, page: Page) -> Dict[str, Any]:
        """Scrape projects (if available)"""
        # LinkedIn projects are rarely public, return empty
        return {'projects': []}

    async def _get_text_from_selectors(self, page: Page, selectors: List[str]) -> Optional[str]:
        """Try multiple selectors to get text content"""
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return None

    async def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.now(timezone.utc)
        hour_ago = now - timedelta(hours=1)
        
        # Clean old requests
        self.request_times = [t for t in self.request_times if t > hour_ago]
        
        # Check limit
        if len(self.request_times) >= self.max_requests_per_hour:
            return False
        
        # Add current request
        self.request_times.append(now)
        return True

    async def _random_delay(self, multiplier: int = 1):
        """Add random delay to avoid detection"""
        delay = random.uniform(self.base_delay, self.max_delay) * multiplier
        await asyncio.sleep(delay)

    async def _get_cached_profile(self, profile_url: str) -> Optional[LinkedInProfile]:
        """Get cached profile"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"linkedin_profile:{hashlib.md5(profile_url.encode()).hexdigest()}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                profile_dict = json.loads(cached_data)
                return LinkedInProfile(**profile_dict)
                
        except Exception as e:
            logger.warning(f"Error retrieving cached profile: {e}")
        
        return None

    async def _cache_profile(self, profile_url: str, profile: LinkedInProfile):
        """Cache profile data"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"linkedin_profile:{hashlib.md5(profile_url.encode()).hexdigest()}"
            cache_data = profile.json()
            
            # Cache for 7 days
            await self.redis_client.setex(cache_key, 604800, cache_data)
            logger.info(f"LinkedIn profile cached: {profile_url}")
            
        except Exception as e:
            logger.warning(f"Error caching profile: {e}")

    def _is_cache_fresh(self, profile: LinkedInProfile) -> bool:
        """Check if cached profile is still fresh (within 24 hours)"""
        if not profile.scraped_at:
            return False
        
        now = datetime.now(timezone.utc)
        cache_age = now - profile.scraped_at
        return cache_age < timedelta(hours=24)

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn profile URL"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc in ['linkedin.com', 'www.linkedin.com'] and 
                   '/in/' in parsed.path)
        except:
            return False

    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy

    async def _rotate_proxy(self):
        """Rotate to next proxy by recreating context"""
        try:
            await self.context.close()
            await self._create_browser_context()
            logger.info("Proxy rotated successfully")
        except Exception as e:
            logger.warning(f"Proxy rotation failed: {e}")

    async def get_user_linkedin_profile(self, user_id: str) -> Optional[LinkedInProfile]:
        """Get user's LinkedIn profile from database"""
        return await self.linkedin_crud.get_user_linkedin(user_id)

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            if self.redis_client:
                await self.redis_client.close()
        except Exception as e:
            logger.warning(f"Error during LinkedIn service cleanup: {e}")


# Global instance
linkedin_service = LinkedInService()


async def initialize_linkedin_service():
    """Initialize the LinkedIn service"""
    if settings.linkedin_scraper_enabled:
        await linkedin_service.initialize()
        logger.info("LinkedInService initialized")
    else:
        logger.info("LinkedInService disabled in configuration")


# Export
__all__ = ['LinkedInService', 'linkedin_service', 'initialize_linkedin_service']
