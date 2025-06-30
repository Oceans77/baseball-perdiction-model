#!/usr/bin/env python3
"""
Comprehensive team data collection and fix script
Usage: python scripts/comprehensive_team_fix.py [--season 2024] [--force-all]
"""

import sys
import os
import pandas as pd
import argparse
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection.api_client import MLBStatsAPI, DataCollector
from features.player_scoring import PlayerScorer
from features.team_scoring import TeamScorer

def deep_api_diagnosis(season=2024):
    """Deeply diagnose what the MLB API is actually returning"""
    print(f"🔍 DEEP API DIAGNOSIS for {season}")
    print("=" * 40)
    
    api = MLBStatsAPI()
    
    # Step 1: Check teams endpoint
    print("1. Testing teams endpoint...")
    teams_df = api.get_teams(season)
    print(f"   Raw API returned {len(teams_df)} teams")
    
    if teams_df.empty:
        print("   ❌ No teams returned from API")
        return None
    
    print("   Teams returned:")
    for _, team in teams_df.iterrows():
        print(f"      {team['team_id']:3d}: {team['team_name']} ({team['abbreviation']})")
    
    # Step 2: Test roster collection for each team
    print(f"\n2. Testing roster collection for each team...")
    team_roster_success = {}
    
    for _, team in teams_df.iterrows():
        team_id = team['team_id']
        team_name = team['team_name']
        
        print(f"   Testing {team_name} (ID: {team_id})...")
        roster_df = api.get_team_roster(team_id, season)
        
        if roster_df.empty:
            print(f"      ❌ No roster data")
            team_roster_success[team_name] = 0
        else:
            print(f"      ✅ {len(roster_df)} players")
            team_roster_success[team_name] = len(roster_df)
        
        time.sleep(0.3)  # Be nice to the API
    
    # Step 3: Test player stats for a few players
    print(f"\n3. Testing player stats collection...")
    successful_teams = [name for name, count in team_roster_success.items() if count > 0]
    print(f"   Teams with rosters: {len(successful_teams)}")
    
    if successful_teams:
        # Test stats for the first successful team
        test_team = successful_teams[0]
        test_team_id = teams_df[teams_df['team_name'] == test_team].iloc[0]['team_id']
        
        print(f"   Testing player stats for {test_team}...")
        roster_df = api.get_team_roster(test_team_id, season)
        
        stats_success = 0
        for i, (_, player) in enumerate(roster_df.head(5).iterrows()):  # Test first 5 players
            player_id = player['player_id']
            player_name = player['full_name']
            
            stats = api.get_player_stats(player_id, season)
            if stats:
                stats_success += 1
                print(f"      ✅ {player_name}: {len(stats)} stats")
            else:
                print(f"      ❌ {player_name}: No stats")
            
            time.sleep(0.2)
        
        print(f"   Stats success rate: {stats_success}/5 players")
    
    return {
        'teams_available': len(teams_df),
        'teams_with_rosters': len(successful_teams),
        'roster_success': team_roster_success
    }

def force_collect_all_teams(season=2024):
    """Force collection of all 30 MLB teams using different approaches"""
    print(f"\n🚀 FORCE COLLECTING ALL TEAMS for {season}")
    print("=" * 45)
    
    api = MLBStatsAPI()
    
    # Approach 1: Try different API parameters
    print("Approach 1: Trying different API parameters...")
    
    # Try without season filter
    teams_noseason = api.get_teams()
    print(f"   No season filter: {len(teams_noseason)} teams")
    
    # Try with specific league IDs
    all_teams = []
    
    # MLB has American League (103) and National League (104)
    for league_id in [103, 104]:
        try:
            url = f"{api.base_url}/teams"
            params = {
                'sportId': 1,  # MLB
                'leagueId': league_id,
                'season': season
            }
            
            response = api.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'teams' in data:
                    league_teams = data['teams']
                    print(f"   League {league_id}: {len(league_teams)} teams")
                    all_teams.extend(league_teams)
        except Exception as e:
            print(f"   League {league_id} failed: {e}")
    
    # Approach 2: Use a known list of team IDs
    print(f"\nApproach 2: Using known MLB team IDs...")
    
    # These are the current 30 MLB team IDs (as of 2024)
    known_team_ids = [
        108, 109, 110, 111, 112, 113, 114, 115, 116, 117,  # AL East + Central
        118, 119, 133, 136, 137, 138, 139, 140, 141, 142,  # AL West + NL East
        143, 144, 145, 146, 147, 158, 120, 121, 134, 135   # NL Central + West
    ]
    
    manual_teams = []
    for team_id in known_team_ids:
        try:
            url = f"{api.base_url}/teams/{team_id}"
            params = {'season': season}
            
            response = api.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'teams' in data and data['teams']:
                    team_info = data['teams'][0]
                    manual_teams.append({
                        'team_id': team_info['id'],
                        'team_name': team_info['name'],
                        'abbreviation': team_info['abbreviation'],
                        'division': team_info.get('division', {}).get('name', ''),
                        'league': team_info.get('league', {}).get('name', '')
                    })
                    print(f"   ✅ {team_info['name']}")
                else:
                    print(f"   ❌ Team ID {team_id}: No data")
            else:
                print(f"   ❌ Team ID {team_id}: HTTP {response.status_code}")
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Team ID {team_id}: {e}")
    
    print(f"\n📊 COLLECTION RESULTS:")
    print(f"   Original API: {len(teams_noseason)} teams")
    print(f"   League approach: {len(all_teams)} teams")
    print(f"   Manual approach: {len(manual_teams)} teams")
    
    # Use the best result
    if len(manual_teams) >= 25:
        best_teams = pd.DataFrame(manual_teams)
        approach = "manual"
    elif len(all_teams) >= 20:
        best_teams = pd.DataFrame([{
            'team_id': team['id'],
            'team_name': team['name'], 
            'abbreviation': team['abbreviation'],
            'division': team.get('division', {}).get('name', ''),
            'league': team.get('league', {}).get('name', '')
        } for team in all_teams])
        approach = "league"
    else:
        best_teams = teams_noseason
        approach = "original"
    
    print(f"\n✅ Using {approach} approach: {len(best_teams)} teams")
    
    # Save the teams data
    os.makedirs("data/raw", exist_ok=True)
    teams_file = f"data/raw/teams_{season}.csv"
    best_teams.to_csv(teams_file, index=False)
    print(f"✅ Saved teams to {teams_file}")
    
    return best_teams

def collect_comprehensive_rosters_and_stats(teams_df, season=2024, max_players_per_team=20):
    """Collect rosters and stats for all teams, with better error handling"""
    print(f"\n📋 COLLECTING COMPREHENSIVE ROSTERS AND STATS")
    print("=" * 50)
    
    api = MLBStatsAPI()
    
    all_rosters = []
    all_stats = []
    
    for _, team in teams_df.iterrows():
        team_id = team['team_id']
        team_name = team['team_name']
        
        print(f"\n🏟️ Processing {team_name} (ID: {team_id})...")
        
        # Get roster
        roster_df = api.get_team_roster(team_id, season)
        if roster_df.empty:
            print(f"   ⚠️ No roster data, skipping...")
            continue
        
        # Add team info to roster
        roster_df['team_name'] = team_name
        roster_df['team_abbreviation'] = team['abbreviation']
        all_rosters.append(roster_df)
        
        print(f"   ✅ Roster: {len(roster_df)} players")
        
        # Get stats for players (limited to avoid timeout)
        players_to_process = min(len(roster_df), max_players_per_team)
        team_stats = []
        
        for i, (_, player) in enumerate(roster_df.head(players_to_process).iterrows()):
            player_id = player['player_id']
            player_name = player['full_name']
            
            # Get player stats
            stats = api.get_player_stats(player_id, season)
            if stats:
                player_data = {
                    'player_id': player_id,
                    'full_name': player_name,
                    'team_name': team_name,
                    'position': player.get('position', ''),
                    'season': season,
                    **stats
                }
                team_stats.append(player_data)
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"      Processed {i + 1}/{players_to_process} players...")
            
            time.sleep(0.1)  # Rate limiting
        
        all_stats.extend(team_stats)
        print(f"   ✅ Stats: {len(team_stats)} players with stats")
        
        time.sleep(0.5)  # Team-level rate limiting
    
    # Save results
    os.makedirs("data/raw/player_stats", exist_ok=True)
    
    if all_rosters:
        combined_rosters = pd.concat(all_rosters, ignore_index=True)
        rosters_file = f"data/raw/player_stats/rosters_{season}.csv"
        combined_rosters.to_csv(rosters_file, index=False)
        print(f"\n✅ Saved {len(combined_rosters)} players to {rosters_file}")
    
    if all_stats:
        stats_df = pd.DataFrame(all_stats)
        stats_file = f"data/raw/player_stats/player_stats_{season}.csv"
        stats_df.to_csv(stats_file, index=False)
        print(f"✅ Saved stats for {len(stats_df)} players to {stats_file}")
        
        teams_with_stats = stats_df['team_name'].nunique()
        print(f"✅ {teams_with_stats} teams have player statistics")
        
        return stats_df
    
    return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Comprehensive team data collection and fix')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--diagnose-only', action='store_true', help='Only run diagnosis')
    parser.add_argument('--force-all', action='store_true', help='Force collection of all 30 teams')
    parser.add_argument('--max-players', type=int, default=15, help='Max players per team to collect stats for')
    
    args = parser.parse_args()
    
    print("🏈 COMPREHENSIVE MLB TEAM DATA FIX")
    print("=" * 35)
    print(f"Season: {args.season}")
    print(f"Max players per team: {args.max_players}")
    
    # Step 1: Deep diagnosis
    diagnosis = deep_api_diagnosis(args.season)
    
    if args.diagnose_only:
        return
    
    if not diagnosis or diagnosis['teams_available'] < 10:
        print(f"\n❌ API diagnosis failed or too few teams available")
        print(f"   Consider trying a different season or checking MLB API status")
        return
    
    # Step 2: Force collect all teams if requested or if we have too few
    if args.force_all or diagnosis['teams_available'] < 25:
        print(f"\n🚀 Force collecting all teams...")
        teams_df = force_collect_all_teams(args.season)
    else:
        # Use existing team data
        teams_file = f"data/raw/teams_{args.season}.csv"
        if os.path.exists(teams_file):
            teams_df = pd.read_csv(teams_file)
        else:
            print(f"❌ No teams file found, collecting...")
            teams_df = force_collect_all_teams(args.season)
    
    if teams_df.empty or len(teams_df) < 10:
        print(f"❌ Failed to collect sufficient team data")
        return
    
    print(f"\n📊 Working with {len(teams_df)} teams")
    
    # Step 3: Collect comprehensive data
    stats_df = collect_comprehensive_rosters_and_stats(teams_df, args.season, args.max_players)
    
    if stats_df.empty:
        print(f"❌ No player statistics collected")
        return
    
    # Step 4: Score everything
    print(f"\n🎯 SCORING PHASE")
    print("=" * 15)
    
    # Clean data
    print("Cleaning data types...")
    numeric_columns = ['avg', 'obp', 'slg', 'ops', 'homeRuns', 'rbi', 'runs', 'hits', 'atBats', 
                       'stolenBases', 'strikeOuts', 'era', 'whip', 'wins', 'losses', 'saves', 
                       'inningsPitched', 'walks', 'fieldingPercentage', 'errors']
    
    for col in numeric_columns:
        if col in stats_df.columns:
            stats_df[col] = pd.to_numeric(stats_df[col], errors='coerce')
    
    # Score players
    print("Scoring players...")
    scorer = PlayerScorer()
    scored_df = scorer.score_all_players(stats_df)
    
    # Save scored players
    os.makedirs("data/processed", exist_ok=True)
    scored_file = f"data/processed/scored_players_{args.season}.csv"
    scored_df.to_csv(scored_file, index=False)
    print(f"✅ Scored players saved to {scored_file}")
    
    # Score teams
    print("Scoring teams...")
    team_scorer = TeamScorer()
    team_scores_df = team_scorer.score_all_teams(scored_df)
    
    # Save team scores
    team_scores_file = f"data/processed/team_scores_{args.season}.csv"
    team_scores_clean = team_scores_df.copy()
    if 'position_breakdown' in team_scores_clean.columns:
        team_scores_clean = team_scores_clean.drop('position_breakdown', axis=1)
    if 'top_players' in team_scores_clean.columns:
        team_scores_clean = team_scores_clean.drop('top_players', axis=1)
    
    team_scores_clean.to_csv(team_scores_file, index=False)
    print(f"✅ Team scores saved to {team_scores_file}")
    
    # Summary
    print(f"\n🎉 COMPREHENSIVE FIX COMPLETE!")
    print("=" * 30)
    print(f"Teams processed: {len(teams_df)}")
    print(f"Players with stats: {len(stats_df)}")
    print(f"Teams with scores: {len(team_scores_df)}")
    
    print(f"\nAvailable teams for matchup analysis:")
    for _, team in team_scores_df.head(10).iterrows():
        print(f"  • {team['team_name']} (Score: {team['overall_score']:.1f})")
    
    if len(team_scores_df) > 10:
        print(f"  ... and {len(team_scores_df) - 10} more teams")
    
    print(f"\n💡 Test your matchup now:")
    print(f"   python scripts/analyze_matchup.py --list-teams --season {args.season}")
    print(f"   python scripts/analyze_matchup.py 'Kansas City Royals' 'Seattle Mariners' --season {args.season}")

if __name__ == "__main__":
    main()
