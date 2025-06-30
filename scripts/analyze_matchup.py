#!/usr/bin/env python3
"""
Team Matchup Analyzer - Detailed head-to-head comparison tool
Usage: python scripts/analyze_matchup.py "Team A" "Team B" [--season 2024] [--detailed]
"""

import sys
import os
import argparse
import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.team_scoring import TeamScorer

class MatchupAnalyzer:
    """
    Comprehensive matchup analysis between two teams
    """
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = data_dir
        self.team_scorer = TeamScorer()
        
    def load_team_data(self, season: int = 2024) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all necessary data for analysis"""
        
        # Load scored players
        players_file = f"{self.data_dir}/scored_players_{season}.csv"
        if not os.path.exists(players_file):
            raise FileNotFoundError(f"Scored players file not found: {players_file}")
        
        players_df = pd.read_csv(players_file)
        
        # Load team scores
        teams_file = f"{self.data_dir}/team_scores_{season}.csv"
        if not os.path.exists(teams_file):
            raise FileNotFoundError(f"Team scores file not found: {teams_file}")
        
        teams_df = pd.read_csv(teams_file)
        
        # Load detailed team data if available
        detailed_file = f"{self.data_dir}/team_scores_detailed_{season}.json"
        detailed_df = pd.DataFrame()
        if os.path.exists(detailed_file):
            with open(detailed_file, 'r') as f:
                detailed_data = json.load(f)
                detailed_df = pd.DataFrame(detailed_data)
        
        return players_df, teams_df, detailed_df
    
    def find_team(self, team_name: str, teams_df: pd.DataFrame) -> Optional[pd.Series]:
        """Find team by name (handles partial matches)"""
        
        # Try exact match first
        exact_match = teams_df[teams_df['team_name'].str.lower() == team_name.lower()]
        if len(exact_match) > 0:
            return exact_match.iloc[0]
        
        # Try partial match
        partial_match = teams_df[teams_df['team_name'].str.lower().str.contains(team_name.lower())]
        if len(partial_match) == 1:
            return partial_match.iloc[0]
        elif len(partial_match) > 1:
            print(f"⚠️  Multiple teams match '{team_name}':")
            for _, team in partial_match.iterrows():
                print(f"   - {team['team_name']}")
            return None
        
        # No match found
        return None
    
    def get_team_roster_analysis(self, team_name: str, players_df: pd.DataFrame) -> Dict:
        """Get detailed roster analysis for a team"""
        
        team_players = players_df[players_df['team_name'] == team_name].copy()
        
        if len(team_players) == 0:
            return {'error': f'No players found for {team_name}'}
        
        # Sort by overall score
        team_players = team_players.sort_values('overall_score', ascending=False)
        
        # Position analysis
        position_stats = {}
        for position in team_players['position'].unique():
            if pd.isna(position) or position == '':
                continue
                
            pos_players = team_players[team_players['position'] == position]
            position_stats[position] = {
                'count': len(pos_players),
                'avg_score': pos_players['overall_score'].mean(),
                'best_player': {
                    'name': pos_players.iloc[0]['full_name'],
                    'score': pos_players.iloc[0]['overall_score'],
                    'batting': pos_players.iloc[0]['batting_score'],
                    'pitching': pos_players.iloc[0]['pitching_score'],
                    'fielding': pos_players.iloc[0]['fielding_score']
                }
            }
        
        # Top performers
        top_players = team_players.head(10)[['full_name', 'position', 'overall_score', 
                                           'batting_score', 'pitching_score', 'fielding_score']].to_dict('records')
        
        # Strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for position, stats in position_stats.items():
            if stats['avg_score'] > 70:
                strengths.append(f"{position} (avg: {stats['avg_score']:.1f})")
            elif stats['avg_score'] < 50:
                weaknesses.append(f"{position} (avg: {stats['avg_score']:.1f})")
        
        return {
            'roster_size': len(team_players),
            'avg_overall_score': team_players['overall_score'].mean(),
            'avg_batting_score': team_players['batting_score'].mean(),
            'avg_pitching_score': team_players['pitching_score'].mean(),
            'avg_fielding_score': team_players['fielding_score'].mean(),
            'position_stats': position_stats,
            'top_players': top_players,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def generate_detailed_matchup(self, team1_name: str, team2_name: str, season: int = 2024) -> Dict:
        """Generate comprehensive matchup analysis"""
        
        # Load data
        players_df, teams_df, detailed_df = self.load_team_data(season)
        
        # Find teams
        team1 = self.find_team(team1_name, teams_df)
        team2 = self.find_team(team2_name, teams_df)
        
        if team1 is None:
            return {'error': f'Team "{team1_name}" not found'}
        if team2 is None:
            return {'error': f'Team "{team2_name}" not found'}
        
        # Get roster analysis
        team1_roster = self.get_team_roster_analysis(team1['team_name'], players_df)
        team2_roster = self.get_team_roster_analysis(team2['team_name'], players_df)
        
        # Generate basic prediction
        prediction = self.team_scorer.generate_matchup_prediction(
            team1.to_dict(), team2.to_dict()
        )
        
        # Enhanced analysis
        analysis = {
            'matchup_info': {
                'team1': team1['team_name'],
                'team2': team2['team_name'],
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'season': season
            },
            'prediction': prediction,
            'team_comparison': {
                'overall_scores': {
                    'team1': team1['overall_score'],
                    'team2': team2['overall_score'],
                    'difference': abs(team1['overall_score'] - team2['overall_score']),
                    'leader': team1['team_name'] if team1['overall_score'] > team2['overall_score'] else team2['team_name']
                },
                'batting_comparison': {
                    'team1': team1['batting_score'],
                    'team2': team2['batting_score'],
                    'difference': abs(team1['batting_score'] - team2['batting_score']),
                    'leader': team1['team_name'] if team1['batting_score'] > team2['batting_score'] else team2['team_name']
                },
                'pitching_comparison': {
                    'team1': team1['pitching_score'],
                    'team2': team2['pitching_score'],
                    'difference': abs(team1['pitching_score'] - team2['pitching_score']),
                    'leader': team1['team_name'] if team1['pitching_score'] > team2['pitching_score'] else team2['team_name']
                },
                'fielding_comparison': {
                    'team1': team1['fielding_score'],
                    'team2': team2['fielding_score'],
                    'difference': abs(team1['fielding_score'] - team2['fielding_score']),
                    'leader': team1['team_name'] if team1['fielding_score'] > team2['fielding_score'] else team2['team_name']
                }
            },
            'roster_analysis': {
                'team1': team1_roster,
                'team2': team2_roster
            },
            'key_matchups': self.identify_key_matchups(team1_roster, team2_roster),
            'game_factors': self.analyze_game_factors(team1, team2)
        }
        
        return analysis
    
    def identify_key_matchups(self, team1_roster: Dict, team2_roster: Dict) -> Dict:
        """Identify key position matchups"""
        
        key_matchups = {}
        
        # Compare positions
        for position in ['Pitcher', 'Catcher', 'First Baseman', 'Shortstop', 'Center Fielder']:
            if position in team1_roster['position_stats'] and position in team2_roster['position_stats']:
                team1_pos = team1_roster['position_stats'][position]
                team2_pos = team2_roster['position_stats'][position]
                
                key_matchups[position] = {
                    'team1_avg': team1_pos['avg_score'],
                    'team2_avg': team2_pos['avg_score'],
                    'advantage': abs(team1_pos['avg_score'] - team2_pos['avg_score']),
                    'leader': 'team1' if team1_pos['avg_score'] > team2_pos['avg_score'] else 'team2'
                }
        
        return key_matchups
    
    def analyze_game_factors(self, team1: pd.Series, team2: pd.Series) -> Dict:
        """Analyze additional game factors"""
        
        factors = {
            'competitiveness': 'High' if abs(team1['overall_score'] - team2['overall_score']) < 5 else 'Medium' if abs(team1['overall_score'] - team2['overall_score']) < 10 else 'Low',
            'expected_scoring': 'High' if (team1['batting_score'] + team2['batting_score']) / 2 > 60 else 'Medium' if (team1['batting_score'] + team2['batting_score']) / 2 > 50 else 'Low',
            'pitching_duel': 'Yes' if (team1['pitching_score'] + team2['pitching_score']) / 2 > 70 else 'No',
            'defensive_game': 'Yes' if (team1['fielding_score'] + team2['fielding_score']) / 2 > 70 else 'No'
        }
        
        return factors

def print_matchup_analysis(analysis: Dict, detailed: bool = False):
    """Print formatted matchup analysis"""
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    info = analysis['matchup_info']
    pred = analysis['prediction']
    comp = analysis['team_comparison']
    
    print(f"\n⚾ MATCHUP ANALYSIS: {info['team1']} vs {info['team2']}")
    print("=" * 60)
    print(f"Analysis Date: {info['analysis_date']}")
    print(f"Season: {info['season']}")
    
    # Prediction
    print(f"\n🔮 PREDICTION")
    print("-" * 20)
    print(f"Predicted Winner: {pred['predicted_winner']}")
    print(f"Win Probability: {pred['win_probability']:.1%}")
    print(f"Confidence: {'High' if pred['win_probability'] > 0.65 else 'Medium' if pred['win_probability'] > 0.55 else 'Low'}")
    
    # Team Comparison
    print(f"\n📊 TEAM COMPARISON")
    print("-" * 25)
    
    # Overall scores
    print(f"Overall Scores:")
    print(f"  {info['team1']:20s}: {comp['overall_scores']['team1']:5.1f}")
    print(f"  {info['team2']:20s}: {comp['overall_scores']['team2']:5.1f}")
    print(f"  Advantage: {comp['overall_scores']['leader']} (+{comp['overall_scores']['difference']:.1f})")
    
    # Component comparison
    print(f"\nComponent Breakdown:")
    components = ['batting', 'pitching', 'fielding']
    for comp_name in components:
        comp_data = comp[f'{comp_name}_comparison']
        print(f"  {comp_name.title():10s}: {comp_data['team1']:5.1f} vs {comp_data['team2']:5.1f} | {comp_data['leader']} (+{comp_data['difference']:.1f})")
    
    # Key advantages
    print(f"\n🎯 KEY ADVANTAGES")
    print("-" * 20)
    for comp_name, data in pred['advantages'].items():
        if data['advantage'] > 2.0:
            print(f"  {comp_name.title():10s}: {data['leader']} (+{data['advantage']:.1f}) - Significant")
        elif data['advantage'] > 1.0:
            print(f"  {comp_name.title():10s}: {data['leader']} (+{data['advantage']:.1f}) - Moderate")
    
    # Game factors
    factors = analysis['game_factors']
    print(f"\n🏟️ GAME FACTORS")
    print("-" * 15)
    print(f"  Competitiveness: {factors['competitiveness']}")
    print(f"  Expected Scoring: {factors['expected_scoring']}")
    print(f"  Pitching Duel: {factors['pitching_duel']}")
    print(f"  Defensive Game: {factors['defensive_game']}")
    
    if detailed:
        print_detailed_analysis(analysis)

def print_detailed_analysis(analysis: Dict):
    """Print detailed roster and matchup analysis"""
    
    roster1 = analysis['roster_analysis']['team1']
    roster2 = analysis['roster_analysis']['team2']
    info = analysis['matchup_info']
    
    print(f"\n📋 DETAILED ROSTER ANALYSIS")
    print("=" * 35)
    
    # Team 1 details
    print(f"\n🏟️ {info['team1']} ROSTER")
    print("-" * 30)
    print(f"Roster Size: {roster1['roster_size']} players")
    print(f"Average Scores: Overall {roster1['avg_overall_score']:.1f} | Batting {roster1['avg_batting_score']:.1f} | Pitching {roster1['avg_pitching_score']:.1f} | Fielding {roster1['avg_fielding_score']:.1f}")
    
    if roster1['strengths']:
        print(f"Strengths: {', '.join(roster1['strengths'])}")
    if roster1['weaknesses']:
        print(f"Weaknesses: {', '.join(roster1['weaknesses'])}")
    
    print(f"\nTop 5 Players:")
    for i, player in enumerate(roster1['top_players'][:5], 1):
        print(f"  {i}. {player['full_name']:20s} ({player['position']:12s}) - {player['overall_score']:4.1f}")
    
    # Team 2 details
    print(f"\n🏟️ {info['team2']} ROSTER")
    print("-" * 30)
    print(f"Roster Size: {roster2['roster_size']} players")
    print(f"Average Scores: Overall {roster2['avg_overall_score']:.1f} | Batting {roster2['avg_batting_score']:.1f} | Pitching {roster2['avg_pitching_score']:.1f} | Fielding {roster2['avg_fielding_score']:.1f}")
    
    if roster2['strengths']:
        print(f"Strengths: {', '.join(roster2['strengths'])}")
    if roster2['weaknesses']:
        print(f"Weaknesses: {', '.join(roster2['weaknesses'])}")
    
    print(f"\nTop 5 Players:")
    for i, player in enumerate(roster2['top_players'][:5], 1):
        print(f"  {i}. {player['full_name']:20s} ({player['position']:12s}) - {player['overall_score']:4.1f}")
    
    # Key matchups
    key_matchups = analysis['key_matchups']
    if key_matchups:
        print(f"\n⚔️ KEY POSITION MATCHUPS")
        print("-" * 25)
        for position, matchup in key_matchups.items():
            if matchup['advantage'] > 3:
                advantage_level = "Major"
            elif matchup['advantage'] > 1:
                advantage_level = "Moderate"
            else:
                advantage_level = "Even"
            
            leader_team = info['team1'] if matchup['leader'] == 'team1' else info['team2']
            print(f"  {position:15s}: {matchup['team1_avg']:4.1f} vs {matchup['team2_avg']:4.1f} | {leader_team} (+{matchup['advantage']:.1f}) - {advantage_level}")

def list_available_teams(data_dir: str = "data/processed", season: int = 2024):
    """List all available teams"""
    
    teams_file = f"{data_dir}/team_scores_{season}.csv"
    if not os.path.exists(teams_file):
        print(f"❌ Team scores file not found: {teams_file}")
        print("   Run 'make score' first to generate team scores.")
        return
    
    teams_df = pd.read_csv(teams_file)
    teams_df = teams_df.sort_values('overall_score', ascending=False)
    
    print(f"\n🏆 AVAILABLE TEAMS ({season} season)")
    print("=" * 40)
    
    for rank, (_, team) in enumerate(teams_df.iterrows(), 1):
        print(f"{rank:2d}. {team['team_name']:25s} (Score: {team['overall_score']:5.1f})")

def main():
    parser = argparse.ArgumentParser(description='Analyze team matchups for upcoming games')
    parser.add_argument('team1', nargs='?', help='First team name')
    parser.add_argument('team2', nargs='?', help='Second team name')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis including rosters')
    parser.add_argument('--list-teams', action='store_true', help='List all available teams')
    parser.add_argument('--data-dir', default='data/processed', help='Data directory')
    parser.add_argument('--save', help='Save analysis to JSON file')
    
    args = parser.parse_args()
    
    if args.list_teams:
        list_available_teams(args.data_dir, args.season)
        return
    
    if not args.team1 or not args.team2:
        print("❌ Please provide two team names")
        print("Usage: python scripts/analyze_matchup.py \"Team A\" \"Team B\"")
        print("\nUse --list-teams to see available teams")
        return
    
    try:
        analyzer = MatchupAnalyzer(args.data_dir)
        analysis = analyzer.generate_detailed_matchup(args.team1, args.team2, args.season)
        
        # Print analysis
        print_matchup_analysis(analysis, args.detailed)
        
        # Save if requested
        if args.save:
            with open(args.save, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\n💾 Analysis saved to {args.save}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure to run the scoring pipeline first:")
        print("   make score")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
