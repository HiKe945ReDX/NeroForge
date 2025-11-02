#!/usr/bin/env python3
"""
GUIDORA CAREER ATLAS EXPANDER - PRODUCTION READY
Fixed version with proper error handling and Vertex AI integration
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    logger.info("✅ Vertex AI SDK loaded")
except ImportError:
    logger.error("❌ Missing Vertex AI SDK")
    logger.error("   Install: pip install google-cloud-aiplatform")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PROJECT_ID = "guidora-main"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash"

# Rate limiting (Gemini Pro: 60 requests/min)
REQUESTS_PER_MINUTE = 50  # Safety margin
SLEEP_BETWEEN_REQUESTS = 60.0 / REQUESTS_PER_MINUTE

# File paths
INPUT_FILE = "careers_database.json"
OUTPUT_FILE = "careers_database_expanded.json"

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def validate_gcp_setup() -> bool:
    """Validate GCP credentials and environment"""
    logger.info("🔍 Validating GCP setup...")
    
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        logger.error("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        logger.error("   Set: export GOOGLE_APPLICATION_CREDENTIALS='/path/to/Guidora-key.json'")
        return False
    
    if not os.path.exists(creds_path):
        logger.error(f"❌ Credentials file not found: {creds_path}")
        return False
    
    logger.info(f"✅ Using credentials: {creds_path}")
    return True


def clean_json_response(text: str) -> str:
    """Remove markdown code blocks from Gemini response"""
    text = text.strip()
    
    # Remove markdown json code blocks
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    
    if text.endswith('```'):
        text = text[:-3]
    
    return text.strip()


def build_expansion_prompt(career: Dict) -> str:
    """Build detailed prompt for Gemini Pro"""
    
    return f"""You are a career guidance expert. Expand this career profile with realistic 2025 US market data.

CURRENT CAREER DATA:
{json.dumps(career, indent=2)}

ADD THESE EXACT FIELDS (return ONLY valid JSON, no markdown):

{{
  "day_in_life": [
    {{"time": "9:00 AM", "activity": "Specific morning task for this exact role"}},
    {{"time": "11:00 AM", "activity": "Mid-morning task"}},
    {{"time": "1:00 PM", "activity": "Afternoon task"}},
    {{"time": "3:00 PM", "activity": "Late afternoon task"}},
    {{"time": "5:00 PM", "activity": "End of day task"}}
  ],
  "top_companies": [
    "Company 1", "Company 2", "Company 3", "Company 4", "Company 5",
    "Company 6", "Company 7", "Company 8", "Company 9", "Company 10"
  ],
  "education": [
    {{"level": "Bachelor's Degree", "field": "Specific major like Computer Science"}},
    {{"level": "Master's Degree (Optional)", "field": "Advanced specialization"}},
    {{"level": "Certifications", "field": "Industry certifications like AWS, Azure"}}
  ],
  "related_careers": [
    "Similar Career Path 1",
    "Similar Career Path 2",
    "Similar Career Path 3",
    "Similar Career Path 4",
    "Similar Career Path 5"
  ],
  "work_environment": {{
    "typical_hours": "40-50 hours per week",
    "setting": "Remote / Hybrid / Office",
    "stress_level": "Low / Medium / High",
    "travel_required": "0-25%"
  }},
  "pros": [
    "Specific advantage 1",
    "Specific advantage 2", 
    "Specific advantage 3",
    "Specific advantage 4",
    "Specific advantage 5"
  ],
  "cons": [
    "Specific challenge 1",
    "Specific challenge 2",
    "Specific challenge 3",
    "Specific challenge 4",
    "Specific challenge 5"
  ],
  "ideal_personality": {{
    "openness": "High / Medium / Low",
    "conscientiousness": "High / Medium / Low",
    "extraversion": "High / Medium / Low",
    "agreeableness": "High / Medium / Low",
    "neuroticism": "High / Medium / Low"
  }}
}}

CRITICAL RULES:
1. Use REAL company names (Google, Microsoft, Amazon, etc.)
2. Make "day_in_life" activities SPECIFIC to this exact role
3. Use 2025 US market realities
4. Return ONLY the JSON object (no markdown, no explanations)
5. Ensure all JSON is valid and properly escaped"""


def expand_single_career(
    career: Dict,
    index: int,
    total: int,
    model: GenerativeModel,
    config: GenerationConfig
) -> Optional[Dict]:
    """Expand a single career profile using Gemini Pro"""
    
    title = career.get('title', 'Unknown')
    career_id = career.get('id', career.get('career_id', 'unknown'))
    
    logger.info('')
    logger.info('=' * 80)
    logger.info(f'📋 [{index}/{total}] Processing: {title}')
    logger.info(f'    Career ID: {career_id}')
    logger.info('=' * 80)
    
    # Build prompt
    prompt = build_expansion_prompt(career)
    
    try:
        logger.info('   🤖 Calling Gemini Pro 2.5 Flash...')
        start_time = time.time()
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=config
        )
        
        elapsed = time.time() - start_time
        logger.info(f'   ✅ Response received in {elapsed:.2f}s')
        
        # Clean and parse response
        response_text = clean_json_response(response.text)
        
        try:
            additions = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f'   ❌ JSON parsing failed: {e}')
            logger.error(f'   Response preview: {response_text[:500]}...')
            return None
        
        # Merge with existing career data
        expanded = dict(career)
        expanded.update(additions)
        
        # Add metadata
        expanded['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        expanded['expanded_by'] = MODEL_NAME
        expanded['expansion_version'] = '2.0'
        
        logger.info(f'   ✨ Successfully added {len(additions)} new fields')
        
        # Estimate cost (approximate)
        input_tokens = len(prompt) // 4
        output_tokens = len(response_text) // 4
        cost = (input_tokens / 1_000_000 * 0.35) + (output_tokens / 1_000_000 * 1.05)
        logger.info(f'   💰 Estimated cost: ${cost:.4f}')
        
        return expanded
        
    except Exception as e:
        logger.error(f'   ❌ Error during expansion: {e}')
        logger.exception('Full traceback:')
        return None


def load_careers(filepath: str) -> List[Dict]:
    """Load careers from JSON file"""
    if not os.path.exists(filepath):
        logger.error(f"❌ File not found: {filepath}")
        logger.error(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common key patterns
        for key in ['tech_careers', 'healthcare_careers', 'business_careers', 
                    'creative_careers', 'education_careers', 'careers']:
            if key in data:
                return data[key]
        # If dict with career objects, return values
        return list(data.values())
    
    logger.error(f"❌ Unsupported JSON structure in {filepath}")
    sys.exit(1)


def save_careers(careers: List[Dict], filepath: str):
    """Save expanded careers to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(careers, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(filepath) / 1024
    logger.info(f"💾 Saved {len(careers)} careers to {filepath}")
    logger.info(f"   File size: {file_size:.1f} KB")


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main(dry_run: bool = False, limit: Optional[int] = None):
    """Main execution function"""
    
    print('')
    print('=' * 80)
    print('🚀 GUIDORA CAREER ATLAS EXPANDER - PRODUCTION')
    print('=' * 80)
    print('')
    
    # Validate GCP setup
    if not validate_gcp_setup():
        sys.exit(1)
    
    # Initialize Vertex AI
    logger.info(f'🔧 Initializing Vertex AI...')
    logger.info(f'   Project: {PROJECT_ID}')
    logger.info(f'   Location: {LOCATION}')
    logger.info(f'   Model: {MODEL_NAME}')
    
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)
        
        # Configure generation
        config = GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=4096
        )
        
        logger.info('✅ Vertex AI initialized successfully')
        
    except Exception as e:
        logger.error(f'❌ Failed to initialize Vertex AI: {e}')
        sys.exit(1)
    
    # Load careers
    logger.info(f'📚 Loading careers from {INPUT_FILE}...')
    careers = load_careers(INPUT_FILE)
    logger.info(f'✅ Loaded {len(careers)} careers')
    
    # Apply limit if specified
    if limit:
        careers = careers[:limit]
        logger.info(f'📊 Limited to first {limit} careers for testing')
    
    # Dry run mode
    if dry_run:
        print('')
        print('=' * 80)
        print('🔍 DRY RUN MODE - No API calls will be made')
        print('=' * 80)
        print(f'   Careers to process: {len(careers)}')
        print(f'   Estimated cost: ${len(careers) * 0.02:.2f}')
        print(f'   Estimated time: {len(careers) * SLEEP_BETWEEN_REQUESTS / 60:.1f} minutes')
        print(f'   Rate limit: {REQUESTS_PER_MINUTE} requests/minute')
        print('')
        print('Sample career:')
        print(json.dumps(careers[0], indent=2))
        print('')
        print('✅ Dry run complete! Remove --dry-run to start expansion.')
        return
    
    # Expand all careers
    print('')
    print('=' * 80)
    print('🚀 STARTING CAREER EXPANSION')
    print('=' * 80)
    
    expanded_careers = []
    success_count = 0
    failed_count = 0
    total_cost = 0.0
    
    for i, career in enumerate(careers, 1):
        expanded = expand_single_career(career, i, len(careers), model, config)
        
        if expanded:
            expanded_careers.append(expanded)
            success_count += 1
        else:
            # Keep original data if expansion fails
            expanded_careers.append(career)
            failed_count += 1
            logger.warning(f'   ⚠️  Keeping original data for {career.get("title")}')
        
        # Rate limiting (except for last request)
        if i < len(careers):
            logger.info(f'   ⏳ Rate limit pause ({SLEEP_BETWEEN_REQUESTS:.1f}s)...')
            time.sleep(SLEEP_BETWEEN_REQUESTS)
    
    # Save results
    logger.info('')
    logger.info('💾 Saving expanded careers...')
    save_careers(expanded_careers, OUTPUT_FILE)
    
    # Final summary
    print('')
    print('=' * 80)
    print('✅ EXPANSION COMPLETE!')
    print('=' * 80)
    print('📊 Statistics:')
    print(f'   - Total careers processed: {len(careers)}')
    print(f'   - Successfully expanded: {success_count}')
    print(f'   - Failed expansions: {failed_count}')
    print(f'   - Success rate: {success_count / len(careers) * 100:.1f}%')
    print(f'   - Estimated total cost: ${len(careers) * 0.02:.2f}')
    print('')
    print('📁 Output:')
    print(f'   - File: {OUTPUT_FILE}')
    print(f'   - Size: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB')
    print('=' * 80)
    print('')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Expand career profiles using Gemini Pro')
    parser.add_argument('--dry-run', action='store_true', help='Test without API calls')
    parser.add_argument('--limit', type=int, help='Limit number of careers to process')
    
    args = parser.parse_args()
    
    try:
        main(dry_run=args.dry_run, limit=args.limit)
    except KeyboardInterrupt:
        logger.warning('')
        logger.warning('⚠️  Expansion interrupted by user (Ctrl+C)')
        logger.warning('   Partial results may have been saved.')
        sys.exit(130)
    except Exception as e:
        logger.error('')
        logger.error(f'❌ Fatal error: {e}')
        logger.exception('Full traceback:')
        sys.exit(1)