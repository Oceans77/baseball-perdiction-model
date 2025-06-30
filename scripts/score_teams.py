#!/usr/bin/env python3
"""
Calculate team scores based on player scores
Usage: python scripts/score_teams.py [--season 2024] [--input-dir data/processed] [--output-dir data/processed]
"""

import sys
import os
import argparse
import pandas as pd
import json
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.team_scoring import TeamScorer

def load_scored_players(input_dir: str, season: int) -> pd.DataFrame:
    """Load scored player data"""
    player_scores_file = f"{input_dir}/scored_players_{season}.csv"
    
    if not os.path.exists(player_scores_file):
        raise FileNotFoundError(f"Scored players file not found: {player_scores_file}")
    
    df = pd.read_csv(player_scores_file)
    print(f"📊 Loaded {len(df)} scored players from {player_scores_file}")
    
    return df

def save_team_scores(team_scores_df: pd.DataFrame, output_dir: str, season: int):
    """Save team scores to CSV and JSON"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main CSV
    csv_file = f"{output_dir}/team_scores_{season}.csv"
    
    # Create a clean version for CSV (remove nested dictionaries)
    csv_data = team_scores_df.copy()
    if 'position_breakdown' in csv_data.columns:
        csv_data = csv_data.drop('position_breakdown', axis=1)
    if 'top_players' in csv_data.columns:
        csv_data = csv_data.drop('top_players', axis=1)
    
    csv_data.to_csv(csv_file, index=False)
    print(f"💾 Saved team scores to {csv_file}")
    
    # Save detailed JSON with all data
    json_file = f"{output_dir}/team_scores_detailed_{season}.json"
    team_scores_dict = team_scores_df.to_dict('records')
    
    with open(json_file, 'w') as f:
        json.dump(team_scores_dict, f, indent=2)
    print(f"💾 Saved detailed team data to {json_file}")
    
    return csv_file, json_file

def generate_team_rankings_report(team_scores_df: pd.DataFrame, season: int):
    """Generate a comprehensive team rankings report"""
    print(f"\n🏆 MLB Team Rankings Report - {season}")
    print("=" * 60)
    
    # Overall rankings
    print(f"\n📈 Overall Team Rankings:")
    print("-" * 40)
    for rank, (_, team) in enumerate(team_scores_df.iterrows(), 1):
        print(f"{rank:2d}. {team['team_name']:20s} | Score: {team['overall_score']:5.1f} | "
              f"Batting: {team['batting_score']:4.1f} | Pitching: {team['pitching_score']:4.1f} | "
              f"Fielding: {team['fielding_score']:4.1f}")
    
    # Component leaders
    print(f"\n🎯 Component Leaders:")
    print("-" * 30)
    
    batting_leader = team_scores_df.loc[team_scores_df['batting_score'].idxmax()]
    pitching_leader = team_scores_df.loc[team_scores_df['pitching_score'].idxmax()]
    fielding_leader = team_scores_df.loc[team_scores_df['fielding_score'].idxmax()]
    
    print(f"Best Batting:  {batting_leader['team_name']} ({batting_leader['batting_score']:.1f})")
    print(f"Best Pitching: {pitching_leader['team_name']} ({pitching_leader['pitching_score']:.1f})")
    print(f"Best Fielding: {fielding_leader['team_name']} ({fielding_leader['fielding_score']:.1f})")
    
    # Statistics
    print(f"\n📊 League Statistics:")
    print("-" * 25)
    print(f"Average team score: {team_scores_df['overall_score'].mean():.2f}")
    print(f"Score range: {team_scores_df['overall_score'].min():.1f} - {team_scores_df['overall_score'].max():.1f}")
    print(f"Standard deviation: {team_scores_df['overall_score'].std():.2f}")
    
    # Tiers
    print(f"\n🏅 Team Tiers:")
    print("-" * 15)
    
    top_tier = team_scores_df[team_scores_df['overall_score'] >= team_scores_df['overall_score'].quantile(0.75)]
    mid_tier = team_scores_df[(team_scores_df['overall_score'] >= team_scores_df['overall_score'].quantile(0.25)) & 
                              (team_scores_df['overall_score'] < team_scores_df['overall_score'].quantile(0.75))]
    bottom_tier = team_scores_df[team_scores_df['overall_score'] < team_scores_df['overall_score'].quantile(0.25)]
    
    print(f"Elite Tier ({len(top_tier)} teams): {', '.join(top_tier['team_name'].tolist())}")
    print(f"Mid Tier ({len(mid_tier)} teams): {', '.join(mid_tier['team_name'].tolist())}")
    print(f"Rebuilding Tier ({len(bottom_tier)} teams): {', '.join(bottom_tier['team_name'].tolist())}")

def generate_sample_predictions(team_scores_df: pd.DataFrame, team_scorer: TeamScorer, num_predictions: int = 5):
    """Generate sample matchup predictions"""
    print(f"\n🔮 Sample Matchup Predictions:")
    print("=" * 45)
    
    # Get top teams for interesting matchups
    top_teams = team_scores_df.head(num_predictions)
    
    predictions = []
    for i in range(len(top_teams) - 1):
        team1 = top_teams.iloc[i].to_dict()
        team2 = top_teams.iloc[i + 1].to_dict()
        
        prediction = team_scorer.generate_matchup_prediction(team1, team2)
        predictions.append(prediction)
        
        print(f"\n{i+1}. {prediction['team1']} vs {prediction['team2']}")
        print(f"   Predicted Winner: {prediction['predicted_winner']} ({prediction['win_probability']:.1%})")
        print(f"   Score Difference: {prediction['score_difference']}")
        
        # Show key advantages
        for component, data in prediction['advantages'].items():
            if data['advantage'] > 1.0:  # Only show significant advantages
                print(f"   {component.title()} Advantage: {data['leader']} (+{data['advantage']:.1f})")
    
    return predictions

def main():
    parser = argparse.ArgumentParser(description='Calculate MLB team scores')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--input-dir', default='data/processed', help='Input directory with scored players')
    parser.add_argument('--output-dir', default='data/processed', help='Output directory')
    parser.add_argument('--predictions', type=int, default=5, help='Number of sample predictions to generate')
    
    args = parser.parse_args()
    
    print(f"🏟️ MLB Team Scoring System - {args.season}")
    print("=" * 40)
    
    try:
        # Load scored player data
        scored_players_df = load_scored_players(args.input_dir, args.season)
        
        # Initialize team scorer
        print(f"\n⚡ Initializing team scorer...")
        team_scorer = TeamScorer()
        
        # Calculate team scores
        print(f"\n🎯 Calculating team scores...")
        team_scores_df = team_scorer.score_all_teams(scored_players_df)
        
        # Save results
        csv_file, json_file = save_team_scores(team_scores_df, args.output_dir, args.season)
        
        # Generate reports
        generate_team_rankings_report(team_scores_df, args.season)
        
        # Generate sample predictions
        if args.predictions > 0:
            generate_sample_predictions(team_scores_df, team_scorer, args.predictions)
        
        print(f"\n🎉 Team scoring completed successfully!")
        print(f"📄 Results saved to:")
        print(f"   - {csv_file}")
        print(f"   - {json_file}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure to run player scoring first: python scripts/score_players.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
