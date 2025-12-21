#!/usr/bin/env python3
"""
Seed initial configurations into the database from config.json.
"""

import asyncio
import json
from pathlib import Path
from sqlmodel import select
from python.database import Config, get_session, init_db


async def seed_configs():
    """Seed initial configurations from config.json into database."""
    
    await init_db()
    
    # Load config.json as the source of truth for seeding
    config_file = Path(__file__).parent.parent / "apps" / "config.json"
    if not config_file.exists():
        config_file = Path(__file__).parent / "config.json"
    
    if config_file.exists():
        with open(config_file) as f:
            file_config = json.load(f)
        print(f"📄 Loaded config from {config_file}")
    else:
        file_config = {}
        print("⚠️  config.json not found, using defaults")
    
    async for session in get_session():
        # Seed auto-apply config from config.json
        result = await session.execute(
            select(Config).where(Config.name == "auto-apply")
        )
        existing = result.scalar_one_or_none()
        
        # Merge jsearch and score_matching from config.json
        auto_apply_data = {
            "jsearch": file_config.get("jsearch", {}),
            "score_matching": file_config.get("score_matching", {})
        }
        
        if not existing:
            # Create from config.json
            auto_apply_config = Config(
                name="auto-apply",
                title="Auto Apply Configuration",
                description="Job search and matching configuration from config.json",
                config_json=json.dumps(auto_apply_data)
            )
            session.add(auto_apply_config)
            print("✅ Created auto-apply configuration from config.json")
        else:
            # Update existing with config.json data
            existing.config_json = json.dumps(auto_apply_data)
            existing.description = "Job search and matching configuration from config.json"
            print("✅ Updated auto-apply configuration from config.json")
        
        # Seed matching_service config (same as score_matching from config.json)
        result = await session.execute(
            select(Config).where(Config.name == "matching_service")
        )
        existing = result.scalar_one_or_none()
        
        matching_data = file_config.get("score_matching", {
            "match_threshold": 70.0,
            "weights": {
                "skills": 0.40,
                "experience": 0.25,
                "role": 0.20,
                "keywords": 0.15
            },
            "auto_generate_resume": True,
            "min_skill_match": 50.0,
            "penalize_overqualified": True,
            "enable_recommendations": True
        })
        
        if not existing:
            matching_config = Config(
                name="matching_service",
                title="Job Matching Service",
                description="Configuration for the job matching algorithm from config.json",
                config_json=json.dumps(matching_data)
            )
            session.add(matching_config)
            print("✅ Created matching_service configuration from config.json")
        else:
            existing.config_json = json.dumps(matching_data)
            print("✅ Updated matching_service configuration from config.json")
        
        await session.commit()
        print("\n✅ Configuration seeding complete! Database is now primary source.")
        print("💡 Tip: Edit configs via /api/configs endpoints or admin UI")


if __name__ == "__main__":
    asyncio.run(seed_configs())
