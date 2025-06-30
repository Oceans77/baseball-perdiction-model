# scripts/collect_data.py
#!/usr/bin/env python3
"""
Main script to collect MLB data
Usage: python scripts/collect_data.py [--season 2024] [--max-players 100]
"""

import sys
import os
import argparse
import yaml
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after adding to path
from data_collection.api_client import DataCollector

def load_config():
    """Load configuration from config file"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Default configuration
        return {
            'data_collection': {
                'season': 2024,
                'max_players_per_run': 100,
                'data_directory': 'data/raw'
            }
        }

def ensure_directories(base_dir: str):
    """Create necessary directories if they don't exist"""
    dirs_to_create = [
        base_dir,
        f"{base_dir}/player_stats",
        f"{base_dir}/team_stats",
        f"{base_dir}/game_results"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description='Collect MLB data')
    parser.add_argument('--season', type=int, help='Season year to collect')
    parser.add_argument('--max-players', type=int, help='Maximum number of players to collect stats for')
    parser.add_argument('--teams-only', action='store_true', help='Only collect team data')
    parser.add_argument('--rosters-only', action='store_true', help='Only collect roster data')
    parser.add_argument('--stats-only', action='store_true', help='Only collect player stats')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    data_config = config['data_collection']
    
    # Override config with command line arguments
    season = args.season or data_config['season']
    max_players = args.max_players or data_config['max_players_per_run']
    data_dir = data_config['data_directory']
    
    # Ensure directories exist
    ensure_directories(data_dir)
    
    # Initialize collector
    collector = DataCollector(data_dir)
    
    print(f"🏈 Starting MLB Data Collection for {season} season")
    print(f"📁 Data directory: {data_dir}")
    print(f"👥 Max players: {max_players}")
    print("=" * 50)
    
    try:
        if not args.rosters_only and not args.stats_only:
            print("\n📋 Step 1: Collecting team information...")
            teams = collector.collect_all_teams(season)
            print(f"✅ Collected {len(teams)} teams")
        
        if not args.teams_only and not args.stats_only:
            print("\n👥 Step 2: Collecting player rosters...")
            rosters = collector.collect_team_rosters(season)
            print(f"✅ Collected {len(rosters)} players")
        
        if not args.teams_only and not args.rosters_only:
            print(f"\n📊 Step 3: Collecting player statistics (max {max_players})...")
            player_stats = collector.collect_player_stats(season, max_players)
            print(f"✅ Collected stats for {len(player_stats)} players")
        
        if not args.rosters_only and not args.stats_only:
            print("\n🏟️ Step 4: Collecting team statistics...")
            team_stats = collector.collect_team_stats(season)
            print(f"✅ Collected stats for {len(team_stats)} teams")
        
        print("\n🎉 Data collection completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Data collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during data collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
