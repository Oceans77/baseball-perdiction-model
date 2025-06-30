# scripts/quick_test.py
#!/usr/bin/env python3
"""
Quick test script to verify data collection is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_collection.api_client import MLBStatsAPI

def test_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing MLB Stats API connection...")
    
    api = MLBStatsAPI()
    
    # Test 1: Get teams
    print("\n1. Testing teams endpoint...")
    teams = api.get_teams(2024)
    if not teams.empty:
        print(f"✅ Successfully retrieved {len(teams)} teams")
        print(f"Sample teams: {teams['team_name'].head(3).tolist()}")
    else:
        print("❌ Failed to retrieve teams")
        return False
    
    # Test 2: Get a single team roster
    print("\n2. Testing roster endpoint...")
    first_team_id = teams.iloc[0]['team_id']
    roster = api.get_team_roster(first_team_id, 2024)
    if not roster.empty:
        print(f"✅ Successfully retrieved roster for team {first_team_id}")
        print(f"Roster size: {len(roster)} players")
        print(f"Sample players: {roster['full_name'].head(3).tolist()}")
    else:
        print("❌ Failed to retrieve roster")
        return False
    
    # Test 3: Get player stats
    print("\n3. Testing player stats endpoint...")
    first_player_id = roster.iloc[0]['player_id']
    stats = api.get_player_stats(first_player_id, 2024)
    if stats:
        print(f"✅ Successfully retrieved stats for player {first_player_id}")
        print(f"Available stats: {list(stats.keys())[:5]}...")
    else:
        print("❌ Failed to retrieve player stats")
        return False
    
    print("\n🎉 All API tests passed! Ready for data collection.")
    return True

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
