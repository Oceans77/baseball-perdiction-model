# src/data_collection/api_client.py

import requests
import pandas as pd
import time
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLBStatsAPI:
    """
    Client for MLB Stats API - free official MLB data source
    """
    
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.session = requests.Session()
        
    def get_teams(self, season: int = 2024) -> pd.DataFrame:
        """Get all MLB teams for a given season"""
        url = f"{self.base_url}/teams"
        params = {
            'sportId': 1,  # MLB
            'season': season
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            teams = []
            for team in data['teams']:
                teams.append({
                    'team_id': team['id'],
                    'team_name': team['name'],
                    'abbreviation': team['abbreviation'],
                    'division': team['division']['name'],
                    'league': team['league']['name']
                })
            
            return pd.DataFrame(teams)
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return pd.DataFrame()
    
    def get_team_roster(self, team_id: int, season: int = 2024) -> pd.DataFrame:
        """Get roster for a specific team"""
        url = f"{self.base_url}/teams/{team_id}/roster"
        params = {'season': season}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            players = []
            for player in data['roster']:
                player_info = player['person']
                position = player.get('position', {})
                
                players.append({
                    'player_id': player_info['id'],
                    'full_name': player_info['fullName'],
                    'first_name': player_info.get('firstName', ''),
                    'last_name': player_info.get('lastName', ''),
                    'position': position.get('name', ''),
                    'position_code': position.get('code', ''),
                    'jersey_number': player.get('jerseyNumber', ''),
                    'team_id': team_id
                })
            
            return pd.DataFrame(players)
        except Exception as e:
            logger.error(f"Error fetching roster for team {team_id}: {e}")
            return pd.DataFrame()
    
    def get_player_stats(self, player_id: int, season: int = 2024, stat_type: str = 'season') -> Dict:
        """Get detailed stats for a specific player"""
        url = f"{self.base_url}/people/{player_id}/stats"
        params = {
            'stats': f'{stat_type}',
            'season': season
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('stats') or not data['stats'][0].get('splits'):
                return {}
            
            stats = data['stats'][0]['splits'][0]['stat']
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching stats for player {player_id}: {e}")
            return {}
    
    def get_team_stats(self, team_id: int, season: int = 2024) -> Dict:
        """Get team-level statistics"""
        # Try different stat types that might work better
        stat_types = ['season', 'seasonAdvanced']
        
        for stat_type in stat_types:
            url = f"{self.base_url}/teams/{team_id}/stats"
            params = {
                'stats': stat_type,
                'season': season,
                'group': 'hitting'  # Focus on hitting stats first
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('stats') and data['stats'][0].get('splits'):
                    stats = data['stats'][0]['splits'][0]['stat']
                    logger.info(f"Successfully retrieved {stat_type} stats for team {team_id}")
                    return stats
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    logger.warning(f"Bad request for team {team_id} with {stat_type} stats, trying alternative...")
                    continue
                else:
                    logger.error(f"HTTP error fetching {stat_type} stats for team {team_id}: {e}")
                    continue
            except Exception as e:
                logger.error(f"Error fetching {stat_type} stats for team {team_id}: {e}")
                continue
        
        # If all stat types fail, try getting basic team info instead
        try:
            url = f"{self.base_url}/teams/{team_id}"
            params = {'season': season}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'teams' in data and data['teams']:
                team_info = data['teams'][0]
                logger.info(f"Retrieved basic info for team {team_id} (no stats available)")
                return {
                    'wins': team_info.get('record', {}).get('wins', 0),
                    'losses': team_info.get('record', {}).get('losses', 0),
                    'winningPercentage': team_info.get('record', {}).get('pct', 0.0)
                }
        except Exception as e:
            logger.error(f"Failed to get any data for team {team_id}: {e}")
        
        return {}

class DataCollector:
    """
    Main data collection orchestrator
    """
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = data_dir
        self.mlb_api = MLBStatsAPI()
        
    def collect_all_teams(self, season: int = 2024) -> pd.DataFrame:
        """Collect information for all MLB teams"""
        logger.info(f"Collecting team data for {season} season...")
        
        teams_df = self.mlb_api.get_teams(season)
        
        if not teams_df.empty:
            # Save to file
            filename = f"{self.data_dir}/teams_{season}.csv"
            teams_df.to_csv(filename, index=False)
            logger.info(f"Saved {len(teams_df)} teams to {filename}")
        
        return teams_df
    
    def collect_team_rosters(self, season: int = 2024) -> pd.DataFrame:
        """Collect rosters for all teams"""
        logger.info(f"Collecting roster data for {season} season...")
        
        # First get all teams
        teams_df = self.mlb_api.get_teams(season)
        all_players = []
        
        for _, team in teams_df.iterrows():
            logger.info(f"Collecting roster for {team['team_name']}...")
            roster_df = self.mlb_api.get_team_roster(team['team_id'], season)
            
            if not roster_df.empty:
                # Add team info to each player
                roster_df['team_name'] = team['team_name']
                roster_df['team_abbreviation'] = team['abbreviation']
                all_players.append(roster_df)
            
            # Be respectful to the API
            time.sleep(0.5)
        
        if all_players:
            combined_rosters = pd.concat(all_players, ignore_index=True)
            
            # Save to file
            filename = f"{self.data_dir}/player_stats/rosters_{season}.csv"
            combined_rosters.to_csv(filename, index=False)
            logger.info(f"Saved {len(combined_rosters)} players to {filename}")
            
            return combined_rosters
        
        return pd.DataFrame()
    
    def collect_player_stats(self, season: int = 2024, max_players: Optional[int] = None) -> pd.DataFrame:
        """Collect detailed statistics for all players"""
        logger.info(f"Collecting player statistics for {season} season...")
        
        # Get roster data first
        rosters_df = pd.read_csv(f"{self.data_dir}/player_stats/rosters_{season}.csv")
        
        if max_players:
            rosters_df = rosters_df.head(max_players)
        
        all_stats = []
        
        for idx, player in rosters_df.iterrows():
            player_id = player['player_id']
            logger.info(f"Collecting stats for {player['full_name']} ({idx+1}/{len(rosters_df)})")
            
            # Get batting stats
            batting_stats = self.mlb_api.get_player_stats(player_id, season, 'season')
            
            if batting_stats:
                # Combine player info with stats
                player_data = {
                    'player_id': player_id,
                    'full_name': player['full_name'],
                    'team_name': player['team_name'],
                    'position': player['position'],
                    'season': season,
                    **batting_stats
                }
                all_stats.append(player_data)
            
            # Be respectful to the API
            time.sleep(0.3)
        
        if all_stats:
            stats_df = pd.DataFrame(all_stats)
            
            # Save to file
            filename = f"{self.data_dir}/player_stats/player_stats_{season}.csv"
            stats_df.to_csv(filename, index=False)
            logger.info(f"Saved stats for {len(stats_df)} players to {filename}")
            
            return stats_df
        
        return pd.DataFrame()
    
    def collect_team_stats(self, season: int = 2024) -> pd.DataFrame:
        """Collect team-level statistics"""
        logger.info(f"Collecting team statistics for {season} season...")
        
        teams_df = pd.read_csv(f"{self.data_dir}/teams_{season}.csv")
        all_team_stats = []
        successful_teams = 0
        failed_teams = []
        
        for _, team in teams_df.iterrows():
            logger.info(f"Collecting stats for {team['team_name']} (ID: {team['team_id']})...")
            
            team_stats = self.mlb_api.get_team_stats(team['team_id'], season)
            
            # Always create a team entry, even if stats are missing
            team_data = {
                'team_id': team['team_id'],
                'team_name': team['team_name'],
                'abbreviation': team['abbreviation'],
                'division': team.get('division', ''),
                'league': team.get('league', ''),
                'season': season,
            }
            
            if team_stats:
                team_data.update(team_stats)
                successful_teams += 1
                logger.info(f"✅ Successfully collected stats for {team['team_name']}")
            else:
                # Add placeholder stats if none available
                team_data.update({
                    'wins': None,
                    'losses': None,
                    'winningPercentage': None,
                    'stats_available': False
                })
                failed_teams.append(team['team_name'])
                logger.warning(f"⚠️ No stats available for {team['team_name']}")
            
            all_team_stats.append(team_data)
            time.sleep(0.5)
        
        # Summary report
        logger.info(f"Team stats collection complete:")
        logger.info(f"✅ Successful: {successful_teams}/{len(teams_df)} teams")
        if failed_teams:
            logger.warning(f"⚠️ Failed teams: {', '.join(failed_teams)}")
        
        if all_team_stats:
            team_stats_df = pd.DataFrame(all_team_stats)
            
            # Save to file
            filename = f"{self.data_dir}/team_stats/team_stats_{season}.csv"
            team_stats_df.to_csv(filename, index=False)
            logger.info(f"Saved data for {len(team_stats_df)} teams to {filename}")
            
            return team_stats_df
        
        return pd.DataFrame()

# Example usage and data collection script
if __name__ == "__main__":
    # Initialize collector
    collector = DataCollector()
    
    # Collect data step by step
    season = 2024
    
    print("=== Starting MLB Data Collection ===")
    
    # 1. Collect teams
    print("\n1. Collecting team information...")
    teams = collector.collect_all_teams(season)
    
    # 2. Collect rosters
    print("\n2. Collecting player rosters...")
    rosters = collector.collect_team_rosters(season)
    
    # 3. Collect player stats (start with a small sample)
    print("\n3. Collecting player statistics...")
    player_stats = collector.collect_player_stats(season, max_players=50)  # Start small
    
    # 4. Collect team stats
    print("\n4. Collecting team statistics...")
    team_stats = collector.collect_team_stats(season)
    
    print("\n=== Data Collection Complete ===")
    print(f"Teams collected: {len(teams) if not teams.empty else 0}")
    print(f"Players collected: {len(rosters) if not rosters.empty else 0}")
    print(f"Player stats collected: {len(player_stats) if not player_stats.empty else 0}")
    print(f"Team stats collected: {len(team_stats) if not team_stats.empty else 0}")
