#!/usr/bin/env python3
"""
Debug script to investigate API issues
Usage: python scripts/debug_api.py [team_id]
"""

import sys
import os
import requests
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def debug_team_stats(team_id: int, season: int = 2024):
    """Debug team stats API call"""
    base_url = "https://statsapi.mlb.com/api/v1"
    
    print(f"🔍 Debugging team {team_id} for season {season}")
    print("=" * 50)
    
    # Test different endpoints and parameters
    test_configs = [
        {"endpoint": f"/teams/{team_id}/stats", "params": {"stats": "season", "season": season}},
        {"endpoint": f"/teams/{team_id}/stats", "params": {"stats": "seasonAdvanced", "season": season}},
        {"endpoint": f"/teams/{team_id}/stats", "params": {"stats": "season", "season": season, "group": "hitting"}},
        {"endpoint": f"/teams/{team_id}/stats", "params": {"stats": "season", "season": season, "group": "pitching"}},
        {"endpoint": f"/teams/{team_id}", "params": {"season": season}},
        {"endpoint": f"/teams/{team_id}", "params": {}},
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}. Testing: {config['endpoint']}")
        print(f"   Parameters: {config['params']}")
        
        url = base_url + config['endpoint']
        
        try:
            response = requests.get(url, params=config['params'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Response keys: {list(data.keys())}")
                
                # Show structure for stats endpoints
                if 'stats' in data and data['stats']:
                    print(f"   Stats groups: {len(data['stats'])}")
                    if data['stats'][0].get('splits'):
                        print(f"   Splits available: {len(data['stats'][0]['splits'])}")
                        if data['stats'][0]['splits']:
                            sample_keys = list(data['stats'][0]['splits'][0].get('stat', {}).keys())
                            print(f"   Sample stat keys: {sample_keys[:5]}...")
                
                # Show team info
                if 'teams' in data and data['teams']:
                    team = data['teams'][0]
                    print(f"   Team: {team.get('name', 'Unknown')}")
                    if 'record' in team:
                        record = team['record']
                        print(f"   Record: {record.get('wins', 0)}-{record.get('losses', 0)}")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def list_all_teams():
    """List all teams to see their IDs"""
    base_url = "https://statsapi.mlb.com/api/v1"
    url = f"{base_url}/teams"
    params = {'sportId': 1, 'season': 2024}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("📋 All MLB Teams (2024):")
        print("=" * 40)
        
        for team in data['teams']:
            print(f"ID: {team['id']:3d} | {team['name']} ({team['abbreviation']})")
            
    except Exception as e:
        print(f"Error listing teams: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            team_id = int(sys.argv[1])
            debug_team_stats(team_id)
        except ValueError:
            print("Please provide a valid team ID number")
            sys.exit(1)
    else:
        print("Usage: python scripts/debug_api.py [team_id]")
        print("\nAvailable teams:")
        list_all_teams()
        print("\nExample: python scripts/debug_api.py 139")
