#!/usr/bin/env python3
import json
import time
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import concurrent.futures

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
except ImportError:
    logger.error("Install: pip install google-cloud-aiplatform")
    sys.exit(1)

PROJECT_ID = "guidora-main"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash"
BATCH_SIZE = 5
TIMEOUT_PER_REQUEST = 30
MAX_RETRIES = 2

INPUT_FILE = "careers_database.json"
OUTPUT_FILE = "careers_database_expanded.json"
CHECKPOINT_FILE = "expansion_checkpoint.json"

class CareerExpander:
    def __init__(self):
        self.model = None
        self.config = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'start_time': datetime.now(),
        }

    def validate_gcp_setup(self) -> bool:
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            logger.error("❌ GOOGLE_APPLICATION_CREDENTIALS not set or invalid")
            return False
        logger.info(f"✅ Using credentials: {creds_path}")
        return True

    def initialize(self):
        if not self.validate_gcp_setup():
            sys.exit(1)
        logger.info(f"🔧 Initializing Vertex AI - Project: {PROJECT_ID}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(MODEL_NAME)
        self.config = GenerationConfig(
            temperature=0.7, top_p=0.95, top_k=40, max_output_tokens=4096
        )
        logger.info("✅ Initialized")

    def build_prompt(self, career: Dict) -> str:
        return f'''You are a career expert. Expand this career with 2025 US market data.
        
CURRENT DATA: {json.dumps(career, indent=2)}

RETURN ONLY VALID JSON (no markdown):
{{
  "day_in_life": [
    {{"time": "9:00 AM", "activity": "Specific task"}},
    {{"time": "11:00 AM", "activity": "Mid-morning"}},
    {{"time": "1:00 PM", "activity": "Afternoon"}},
    {{"time": "3:00 PM", "activity": "Late afternoon"}},
    {{"time": "5:00 PM", "activity": "End of day"}}
  ],
  "top_companies": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Salesforce", "Adobe", "Oracle", "IBM"],
  "education": [
    {{"level": "Bachelor's", "field": "Computer Science"}},
    {{"level": "Master's (Optional)", "field": "Advanced specialization"}},
    {{"level": "Certifications", "field": "Industry certs"}}
  ],
  "related_careers": ["Career 1", "Career 2", "Career 3", "Career 4", "Career 5"],
  "work_environment": {{"typical_hours": "40-50", "setting": "Remote/Hybrid", "stress_level": "Medium", "travel_required": "0-25%"}},
  "pros": ["Advantage 1", "Advantage 2", "Advantage 3", "Advantage 4", "Advantage 5"],
  "cons": ["Challenge 1", "Challenge 2", "Challenge 3", "Challenge 4", "Challenge 5"],
  "ideal_personality": {{"openness": "High", "conscientiousness": "High", "extraversion": "Medium", "agreeableness": "Medium", "neuroticism": "Low"}}
}}'''

    def expand_career(self, career: Dict, retry_count: int = 0) -> Optional[Dict]:
        try:
            prompt = self.build_prompt(career)
            response = self.model.generate_content(prompt, generation_config=self.config)
            text = response.text.strip()
            if text.startswith('```
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]
            if text.endswith('```
                text = text[:-3]
            additions = json.loads(text.strip())
            expanded = {**career, **additions}
            expanded['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            expanded['expanded_by'] = MODEL_NAME
            self.stats['success'] += 1
            return expanded
        except Exception as e:
            if retry_count < MAX_RETRIES:
                logger.warning(f"⚠️  Retry {retry_count + 1} for {career.get('title')}")
                time.sleep(2 ** retry_count)
                return self.expand_career(career, retry_count + 1)
            self.stats['failed'] += 1
            logger.error(f"❌ Failed: {career.get('title')} - {e}")
            return career

    def load_careers(self, filepath: str) -> List[Dict]:
        if not os.path.exists(filepath):
            logger.error(f"❌ File not found: {filepath}")
            sys.exit(1)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for key in ['tech_careers', 'careers']:
                if key in data:
                    return data[key]
            return list(data.values())
        sys.exit(1)

    def save_checkpoint(self, careers: List[Dict]):
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'processed': len([c for c in careers if 'expanded_by' in c]),
                'timestamp': datetime.now().isoformat(),
                'careers': careers
            }, f)

    def save_careers(self, careers: List[Dict]):
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(careers, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved to {OUTPUT_FILE}")

    def process_batch(self, careers: List[Dict], batch_size: int = BATCH_SIZE) -> List[Dict]:
        expanded = []
        total = len(careers)
        print("\n" + "="*80)
        print("🚀 STARTING EXPANSION")
        print("="*80 + "\n")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {}
            for i, career in enumerate(careers):
                future = executor.submit(self.expand_career, career)
                futures[future] = i + 1
            
            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                result = future.result()
                expanded.append(result)
                pct = (len(expanded) / total) * 100
                print(f"\r[{len(expanded)}/{total}] {pct:.1f}% | Success: {self.stats['success']} | Failed: {self.stats['failed']}", end='')
                if len(expanded) % 10 == 0:
                    self.save_checkpoint(expanded)
        
        print("\n")
        return expanded

    def run(self, limit: Optional[int] = None, dry_run: bool = False):
        self.initialize()
        careers = self.load_careers(INPUT_FILE)
        if limit:
            careers = careers[:limit]
        self.stats['total'] = len(careers)
        
        if dry_run:
            print(f"\n🔍 DRY RUN: {len(careers)} careers")
            print(f"Est. time: {len(careers) * 2}s")
            return
        
        expanded_careers = self.process_batch(careers)
        self.save_careers(expanded_careers)
        
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        print("\n" + "="*80)
        print("✅ COMPLETE!")
        print("="*80)
        print(f"📊 Success: {self.stats['success']}/{self.stats['total']}")
        print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/self.stats['total']:.2f}s/career)")
        print("="*80 + "\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    
    try:
        expander = CareerExpander()
        expander.run(limit=args.limit, dry_run=args.dry_run)
    except KeyboardInterrupt:
        logger.warning("⚠️  Interrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.exception('Full traceback:')
        sys.exit(1)
