#!/usr/bin/env python3
"""
Fix matchup teams availability issue
Usage: python scripts/fix_matchup_teams.py [--season 2024]
"""

import sys
import os
import pandas as pd
import argparse

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection.api_client import DataCollector
from features.player_scoring import PlayerScorer
from features.team_scoring import TeamScorer

def diagnose_team_pipeline(season=2024):
    """Diagnose where teams are lost in the pipeline"""
    print(f"🔍 Diagnosing Team Pipeline for {season}")
    print("=" * 40)
    
    # Step 1: Check raw teams
    teams_file = f"data/raw/teams_{season}.csv"
    if os.path.exists(teams_file):
        teams_df = pd.read_csv(teams_file)
        print(f"✅ Raw teams: {len(teams_df)} teams")
        raw_teams = set(teams_df['team_name'].tolist())
    else:
        print(f"❌ No raw teams file found")
        return False
    
    # Step 2: Check player rosters
    rosters_file = f"data/raw/player_stats/rosters_{season}.csv"
    if os.path.exists(rosters_file):
        rosters_df = pd.read_csv(rosters_file)
        roster_teams = set(rosters_df['team_name'].unique())
        print(f"✅ Teams with rosters: {len(roster_teams)} teams")
        
        missing_roster_teams = raw_teams - roster_teams
        if missing_roster_teams:
            print(f"⚠️  Teams missing rosters: {missing_roster_teams}")
    else:
        print(f"❌ No rosters file found")
        roster_teams = set()
    
    # Step 3: Check player stats
    stats_file = f"data/raw/player_stats/player_stats_{season}.csv"
    if os.path.exists(stats_file):
        stats_df = pd.read_csv(stats_file)
        stats_teams = set(stats_df['team_name'].unique())
        print(f"✅ Teams with player stats: {len(stats_teams)} teams")
        
        missing_stats_teams = raw_teams - stats_teams
        if missing_stats_teams:
            print(f"⚠️  Teams missing player stats: {missing_stats_teams}")
    else:
        print(f"❌ No player stats file found")
        stats_teams = set()
    
    # Step 4: Check scored players
    scored_file = f"data/processed/scored_players_{season}.csv"
    if os.path.exists(scored_file):
        scored_df = pd.read_csv(scored_file)
        scored_teams = set(scored_df['team_name'].unique())
        print(f"✅ Teams with scored players: {len(scored_teams)} teams")
        
        missing_scored_teams = raw_teams - scored_teams
        if missing_scored_teams:
            print(f"⚠️  Teams missing scored players: {missing_scored_teams}")
    else:
        print(f"❌ No scored players file found")
        scored_teams = set()
    
    # Step 5: Check team scores
    team_scores_file = f"data/processed/team_scores_{season}.csv"
    if os.path.exists(team_scores_file):
        team_scores_df = pd.read_csv(team_scores_file)
        final_teams = set(team_scores_df['team_name'].tolist())
        print(f"✅ Teams with final scores: {len(final_teams)} teams")
        
        missing_final_teams = raw_teams - final_teams
        if missing_final_teams:
            print(f"⚠️  Teams missing final scores: {missing_final_teams}")
    else:
        print(f"❌ No team scores file found")
        final_teams = set()
    
    # Summary
    print(f"\n📊 PIPELINE SUMMARY:")
    print(f"Raw teams:        {len(raw_teams)}")
    print(f"Teams w/ rosters: {len(roster_teams)}")
    print(f"Teams w/ stats:   {len(stats_teams)}")
    print(f"Teams scored:     {len(scored_teams)}")
    print(f"Final teams:      {len(final_teams)}")
    
    return {
        'raw_teams': raw_teams,
        'roster_teams': roster_teams,
        'stats_teams': stats_teams,
        'scored_teams': scored_teams,
        'final_teams': final_teams
    }

def fix_missing_teams(season=2024, target_teams=None):
    """Fix missing teams by ensuring they have data through the pipeline"""
    print(f"\n🔧 Fixing Missing Teams for {season}")
    print("=" * 35)
    
    # Check if this season's data is available from MLB API
    from data_collection.api_client import MLBStatsAPI
    
    print("Checking MLB API availability for this season...")
    api = MLBStatsAPI()
    test_teams = api.get_teams(season)
    
    if test_teams.empty:
        print(f"❌ MLB API has no data for {season} season yet")
        print(f"   This usually means:")
        print(f"   - The {season} season hasn't started")
        print(f"   - MLB hasn't released official team rosters yet")
        print(f"   - API data isn't available for future seasons")
        print(f"\n💡 Try using the most recent available season (usually {season-1})")
        return False
    
    print(f"✅ MLB API has data for {len(test_teams)} teams in {season}")
    
    collector = DataCollector()
    
    # If specific teams requested, focus on those
    if target_teams:
        print(f"Focusing on teams: {target_teams}")
        
        # Check if these teams exist in raw data
        teams_file = f"data/raw/teams_{season}.csv"
        if os.path.exists(teams_file):
            teams_df = pd.read_csv(teams_file)
            available_teams = teams_df['team_name'].tolist()
            
            missing_teams = [t for t in target_teams if not any(t.lower() in team.lower() for team in available_teams)]
            if missing_teams:
                print(f"❌ These teams not found in raw data: {missing_teams}")
                print("Available teams:", available_teams)
                return False
    
    # Step 1: Ensure we have all rosters
    print("Step 1: Collecting/updating team rosters...")
    try:
        rosters_df = collector.collect_team_rosters(season)
        if rosters_df.empty:
            print("❌ Failed to collect rosters - may be too early in season")
            return False
        print(f"✅ Rosters collected for {rosters_df['team_name'].nunique()} teams")
    except Exception as e:
        print(f"❌ Error collecting rosters: {e}")
        return False
    
    # Step 2: Collect more player stats to ensure all teams represented
    print("Step 2: Collecting more player statistics...")
    try:
        stats_df = collector.collect_player_stats(season, max_players=400)  # Increased limit
        if stats_df.empty:
            print("❌ Failed to collect player stats - may be too early in season")
            return False
        print(f"✅ Stats collected for {stats_df['team_name'].nunique()} teams")
    except Exception as e:
        print(f"❌ Error collecting player stats: {e}")
        print("   This often happens early in the season when stats aren't available yet")
        return False
    
    # Step 3: Re-score all players
    print("Step 3: Scoring all players...")
    scorer = PlayerScorer()
    
    # Load the updated player stats
    stats_file = f"data/raw/player_stats/player_stats_{season}.csv"
    if not os.path.exists(stats_file):
        print("❌ Player stats file not found after collection")
        return False
    
    updated_stats_df = pd.read_csv(stats_file)
    
    # Clean the data - convert numeric columns to proper types
    print("   Cleaning and converting data types...")
    numeric_columns = ['avg', 'obp', 'slg', 'ops', 'homeRuns', 'rbi', 'runs', 'hits', 'atBats', 
                       'stolenBases', 'strikeOuts', 'era', 'whip', 'wins', 'losses', 'saves', 
                       'inningsPitched', 'walks', 'fieldingPercentage', 'errors', 'assists', 'putOuts']
    
    for col in numeric_columns:
        if col in updated_stats_df.columns:
            # Convert to numeric, errors='coerce' turns invalid values to NaN
            updated_stats_df[col] = pd.to_numeric(updated_stats_df[col], errors='coerce')
    
    print(f"   Data cleaned - {len(updated_stats_df)} players ready for scoring")
    
    scored_df = scorer.score_all_players(updated_stats_df)
    
    # Save scored players
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    scored_file = f"{output_dir}/scored_players_{season}.csv"
    scored_df.to_csv(scored_file, index=False)
    print(f"✅ Scored {len(scored_df)} players from {scored_df['team_name'].nunique()} teams")
    
    # Step 4: Re-score all teams
    print("Step 4: Scoring all teams...")
    team_scorer = TeamScorer()
    team_scores_df = team_scorer.score_all_teams(scored_df)
    
    # Save team scores
    csv_file = f"{output_dir}/team_scores_{season}.csv"
    
    # Clean version for CSV
    csv_data = team_scores_df.copy()
    if 'position_breakdown' in csv_data.columns:
        csv_data = csv_data.drop('position_breakdown', axis=1)
    if 'top_players' in csv_data.columns:
        csv_data = csv_data.drop('top_players', axis=1)
    
    csv_data.to_csv(csv_file, index=False)
    print(f"✅ Scored {len(team_scores_df)} teams")
    
    return True

def test_matchup_analyzer(season=2024):
    """Test the matchup analyzer to see available teams"""
    print(f"\n🧪 Testing Matchup Analyzer for {season}")
    print("=" * 40)
    
    try:
        # Try to list available teams directly
        teams_file = f"data/processed/team_scores_{season}.csv"
        if not os.path.exists(teams_file):
            print(f"❌ Team scores file not found: {teams_file}")
            return False
        
        teams_df = pd.read_csv(teams_file)
        teams_df = teams_df.sort_values('overall_score', ascending=False)
        
        print(f"✅ Found {len(teams_df)} teams available for matchup analysis:")
        print("-" * 50)
        
        for rank, (_, team) in enumerate(teams_df.iterrows(), 1):
            print(f"{rank:2d}. {team['team_name']:25s} (Score: {team['overall_score']:5.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing matchup analyzer: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix matchup teams availability')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--diagnose-only', action='store_true', help='Only diagnose, do not fix')
    parser.add_argument('--target-teams', nargs='+', help='Specific teams to focus on')
    
    args = parser.parse_args()
    
    print("🏈 Fix Matchup Teams Tool")
    print("=" * 25)
    
    # Special handling for 2025 or future seasons
    if args.season >= 2025:
        print(f"⚠️  You're requesting {args.season} season data.")
        print("   Note: MLB typically doesn't release complete data until spring training.")
        print("   If this fails, try using 2024 data instead.")
        print()
    
    # Always diagnose first
    pipeline_info = diagnose_team_pipeline(args.season)
    
    if not pipeline_info:
        print(f"\n❌ No data found for {args.season} season.")
        if args.season >= 2025:
            print(f"💡 Suggestion: Try with --season 2024 for the most recent complete data")
            print(f"   python scripts/fix_matchup_teams.py --season 2024")
        else:
            print(f"💡 Try collecting data first:")
            print(f"   python scripts/collect_data.py --season {args.season}")
        return
    
    if args.diagnose_only:
        return
    
    # Check if fix is needed
    if len(pipeline_info['final_teams']) >= 25:  # Most teams available
        print(f"\n✅ Most teams already available ({len(pipeline_info['final_teams'])}/30)")
        print("Testing matchup analyzer...")
        test_matchup_analyzer(args.season)
        return
    
    # Fix the pipeline
    print(f"\n🛠️ Only {len(pipeline_info['final_teams'])} teams available for matchups.")
    print("Fixing the pipeline...")
    
    success = fix_missing_teams(args.season, args.target_teams)
    
    if success:
        print(f"\n✅ Fix completed! Testing results...")
        
        # Re-diagnose to show improvement
        new_pipeline_info = diagnose_team_pipeline(args.season)
        
        # Test matchup analyzer
        test_matchup_analyzer(args.season)
        
        print(f"\n🎉 You should now have {len(new_pipeline_info['final_teams'])} teams available for matchup analysis!")
        print(f"Try: python scripts/analyze_matchup.py --list-teams --season {args.season}")
    else:
        print(f"\n❌ Fix failed for {args.season} season.")
        
        if args.season >= 2025:
            print(f"\n💡 This is likely because {args.season} season data isn't available yet.")
            print(f"   Try using the most recent complete season:")
            print(f"   python scripts/fix_matchup_teams.py --season 2024")
            print(f"   python scripts/analyze_matchup.py 'Kansas City Royals' 'Seattle Mariners' --season 2024")
        else:
            print(f"   You may need to:")
            print(f"1. Run: python scripts/collect_data.py --season {args.season} --max-players 500")
            print(f"2. Then: python scripts/score_players.py --season {args.season}")
            print(f"3. Then: python scripts/score_teams.py --season {args.season}")

if __name__ == "__main__":
    main()
