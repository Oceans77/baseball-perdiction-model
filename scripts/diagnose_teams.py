#!/usr/bin/env python3
"""
Diagnostic script to check team data completeness and fix missing teams
Usage: python scripts/diagnose_teams.py [--season 2025] [--fix]
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection.api_client import MLBStatsAPI, DataCollector

def get_current_season():
    """Get the current MLB season year"""
    now = datetime.now()
    # MLB season typically runs Feb-Oct, so if we're past October, it's next year's data prep
    if now.month >= 11:
        return now.year + 1
    return now.year

def check_team_data(season=None):
    """Check what team data we currently have"""
    if season is None:
        season = get_current_season()
    
    print(f"🔍 Diagnosing Team Data for {season} Season")
    print("=" * 40)
    
    # Check raw team data
    teams_file = f"data/raw/teams_{season}.csv"
    if os.path.exists(teams_file):
        teams_df = pd.read_csv(teams_file)
        print(f"✅ Raw teams file found: {len(teams_df)} teams")
        print(f"Teams: {teams_df['team_name'].tolist()}")
    else:
        print(f"❌ Raw teams file not found: {teams_file}")
        return False
    
    # Check scored players
    players_file = f"data/processed/scored_players_{season}.csv"
    if os.path.exists(players_file):
        players_df = pd.read_csv(players_file)
        unique_teams = players_df['team_name'].nunique()
        print(f"✅ Scored players found: {len(players_df)} players from {unique_teams} teams")
        print(f"Teams with players: {sorted(players_df['team_name'].unique())}")
    else:
        print(f"❌ Scored players file not found: {players_file}")
    
    # Check team scores
    scores_file = f"data/processed/team_scores_{season}.csv"
    if os.path.exists(scores_file):
        scores_df = pd.read_csv(scores_file)
        print(f"✅ Team scores found: {len(scores_df)} teams")
        print(f"Teams with scores: {scores_df['team_name'].tolist()}")
    else:
        print(f"❌ Team scores file not found: {scores_file}")
    
    return True

def get_all_mlb_teams(season=None):
    """Get all 30 MLB teams from the API"""
    if season is None:
        season = get_current_season()
    
    print(f"\n🏟️ Fetching All MLB Teams for {season} Season")
    print("=" * 45)
    
    api = MLBStatsAPI()
    teams_df = api.get_teams(season)
    
    if teams_df.empty:
        print(f"❌ Failed to fetch teams from API for {season}")
        print("   This might be because the season hasn't started yet or data isn't available")
        return None
    
    print(f"✅ Retrieved {len(teams_df)} teams from MLB API:")
    for _, team in teams_df.iterrows():
        print(f"   {team['team_name']} ({team['abbreviation']})")
    
    return teams_df

def fix_team_data(season=None):
    """Fix missing team data"""
    if season is None:
        season = get_current_season()
    
    print(f"\n🔧 Fixing Team Data for {season} Season")
    print("=" * 35)
    
    # Initialize collector
    collector = DataCollector()
    
    # Step 1: Collect all teams
    print(f"Step 1: Collecting all teams for {season}...")
    teams_df = collector.collect_all_teams(season)
    
    if teams_df.empty:
        print(f"❌ Failed to collect teams for {season}")
        print("   This might be because:")
        print("   - The season hasn't started yet")
        print("   - MLB API doesn't have data for this season")
        print("   - Network connectivity issues")
        return False
    
    print(f"✅ Collected {len(teams_df)} teams")
    
    # Step 2: Collect rosters for all teams
    print(f"Step 2: Collecting rosters for all teams in {season}...")
    rosters_df = collector.collect_team_rosters(season)
    
    if rosters_df.empty:
        print(f"❌ Failed to collect rosters for {season}")
        print("   This might be because rosters aren't finalized yet")
        return False
    
    print(f"✅ Collected {len(rosters_df)} players")
    
    # Step 3: Collect player stats (limited to avoid long wait)
    print(f"Step 3: Collecting player stats for {season} (limited sample)...")
    stats_df = collector.collect_player_stats(season, max_players=200)
    
    if stats_df.empty:
        print(f"❌ Failed to collect player stats for {season}")
        print("   This might be because the season hasn't started or stats aren't available yet")
        return False
    
    print(f"✅ Collected stats for {len(stats_df)} players")
    
    return True

def check_specific_teams(team_names, season=None):
    """Check if specific teams are available"""
    if season is None:
        season = get_current_season()
    
    print(f"\n🔍 Checking Specific Teams for {season}: {', '.join(team_names)}")
    print("=" * 60)
    
    # Load team data
    teams_file = f"data/raw/teams_{season}.csv"
    if not os.path.exists(teams_file):
        print(f"❌ No team data found for {season}. Run with --fix first.")
        return
    
    teams_df = pd.read_csv(teams_file)
    
    for team_name in team_names:
        # Try to find the team
        matches = teams_df[teams_df['team_name'].str.contains(team_name, case=False, na=False)]
        
        if len(matches) == 0:
            print(f"❌ '{team_name}' not found in {season}")
        elif len(matches) == 1:
            team = matches.iloc[0]
            print(f"✅ '{team_name}' found: {team['team_name']} ({team['abbreviation']})")
        else:
            print(f"⚠️  Multiple matches for '{team_name}' in {season}:")
            for _, team in matches.iterrows():
                print(f"    - {team['team_name']} ({team['abbreviation']})")

def list_available_seasons():
    """List what seasons we have data for"""
    print(f"\n📅 Available Seasons")
    print("=" * 20)
    
    seasons_found = []
    
    # Check data/raw for team files
    raw_dir = "data/raw"
    if os.path.exists(raw_dir):
        for file in os.listdir(raw_dir):
            if file.startswith("teams_") and file.endswith(".csv"):
                try:
                    season = int(file.split("_")[1].split(".")[0])
                    seasons_found.append(season)
                except ValueError:
                    continue
    
    # Check data/processed for scored files
    processed_dir = "data/processed" 
    if os.path.exists(processed_dir):
        for file in os.listdir(processed_dir):
            if file.startswith("team_scores_") and file.endswith(".csv"):
                try:
                    season = int(file.split("_")[2].split(".")[0])
                    if season not in seasons_found:
                        seasons_found.append(season)
                except ValueError:
                    continue
    
    if seasons_found:
        seasons_found = sorted(set(seasons_found))
        print(f"Found data for seasons: {seasons_found}")
        
        for season in seasons_found:
            teams_file = f"data/raw/teams_{season}.csv"
            scores_file = f"data/processed/team_scores_{season}.csv"
            
            status = []
            if os.path.exists(teams_file):
                status.append("teams")
            if os.path.exists(scores_file):
                status.append("scores")
            
            print(f"  {season}: {', '.join(status) if status else 'incomplete'}")
    else:
        print("No season data found")
    
    return seasons_found

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose and fix team data issues')
    parser.add_argument('--season', type=int, help=f'Season year (default: {get_current_season()})')
    parser.add_argument('--fix', action='store_true', help='Fix missing team data')
    parser.add_argument('--check', nargs='+', help='Check specific team names')
    parser.add_argument('--list-seasons', action='store_true', help='List available seasons')
    
    args = parser.parse_args()
    
    current_season = get_current_season()
    season = args.season or current_season
    
    print("🏈 MLB Team Data Diagnostic Tool")
    print("=" * 35)
    print(f"Current season: {current_season}")
    print(f"Analyzing season: {season}")
    
    # List seasons if requested
    if args.list_seasons:
        list_available_seasons()
        return
    
    # Always check current state first
    check_team_data(season)
    
    # Check specific teams if requested
    if args.check:
        check_specific_teams(args.check, season)
    
    # Fix data if requested
    if args.fix:
        print(f"\n🛠️ Fixing team data for {season}...")
        if fix_team_data(season):
            print(f"\n✅ Team data fix completed for {season}!")
            print(f"Next steps:")
            print(f"1. python scripts/score_players.py --season {season}")
            print(f"2. python scripts/score_teams.py --season {season}")
            print(f"3. python scripts/analyze_matchup.py --list-teams --season {season}")
        else:
            print(f"\n❌ Failed to fix team data for {season}")
            if season > current_season:
                print(f"   Note: {season} season may not have started yet or data may not be available")
    
    # Show next steps
    if not args.fix:
        print(f"\n📋 Next Steps:")
        print(f"1. Run: python scripts/diagnose_teams.py --season {season} --fix")
        print(f"2. Re-run scoring: python scripts/score_players.py --season {season}")
        print(f"3. Score teams: python scripts/score_teams.py --season {season}")
        print(f"4. Test matchup: python scripts/analyze_matchup.py --list-teams --season {season}")

if __name__ == "__main__":
    main()
