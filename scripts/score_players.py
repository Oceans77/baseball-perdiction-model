#!/usr/bin/env python3
"""
Score players based on their statistics
Usage: python scripts/score_players.py [--season 2024] [--output-dir data/processed]
"""

import sys
import os
import argparse
import pandas as pd
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.player_scoring import PlayerScorer

def load_player_data(data_dir: str, season: int) -> pd.DataFrame:
    """Load player statistics data"""
    player_stats_file = f"{data_dir}/raw/player_stats/player_stats_{season}.csv"
    
    if not os.path.exists(player_stats_file):
        raise FileNotFoundError(f"Player stats file not found: {player_stats_file}")
    
    df = pd.read_csv(player_stats_file)
    print(f"📊 Loaded {len(df)} players from {player_stats_file}")
    
    return df

def analyze_data_quality(df: pd.DataFrame):
    """Analyze the quality and completeness of the data"""
    print("\n🔍 Data Quality Analysis:")
    print("=" * 40)
    
    # Check for key columns
    key_columns = ['avg', 'obp', 'slg', 'ops', 'homeRuns', 'era', 'whip', 'strikeOuts']
    
    for col in key_columns:
        if col in df.columns:
            non_null_count = df[col].notna().sum()
            percentage = (non_null_count / len(df)) * 100
            print(f"{col:12s}: {non_null_count:3d}/{len(df)} ({percentage:5.1f}%) players have data")
        else:
            print(f"{col:12s}: Column not found")
    
    # Position distribution
    print(f"\n📍 Position Distribution:")
    if 'position' in df.columns:
        position_counts = df['position'].value_counts()
        for pos, count in position_counts.head(10).items():
            print(f"  {pos:15s}: {count:3d} players")
    
    # Team distribution
    print(f"\n🏟️ Team Distribution:")
    if 'team_name' in df.columns:
        team_counts = df['team_name'].value_counts()
        print(f"  Players across {len(team_counts)} teams")
        print(f"  Average per team: {len(df) / len(team_counts):.1f} players")

def save_scored_data(scored_df: pd.DataFrame, output_dir: str, season: int):
    """Save scored player data"""
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/scored_players_{season}.csv"
    scored_df.to_csv(output_file, index=False)
    print(f"💾 Saved scored data to {output_file}")
    
    return output_file

def generate_summary_report(scored_df: pd.DataFrame, season: int, show_all_scores: bool = False):
    """Generate a summary report of the scoring results"""
    print(f"\n📈 Player Scoring Summary Report - {season}")
    print("=" * 50)
    
    # Overall statistics
    print(f"Total players scored: {len(scored_df)}")
    print(f"Average overall score: {scored_df['overall_score'].mean():.2f}")
    print(f"Score range: {scored_df['overall_score'].min():.2f} - {scored_df['overall_score'].max():.2f}")
    
    # Top performers
    print(f"\n🏆 Top 10 Players Overall:")
    top_players = scored_df.nlargest(10, 'overall_score')[['full_name', 'team_name', 'position', 'overall_score']]
    for idx, player in top_players.iterrows():
        print(f"  {player['overall_score']:5.1f} | {player['full_name']:20s} | {player['team_name']} ({player['position']})")
    
    if show_all_scores:
        print(f"\n📊 DETAILED SCORE BREAKDOWN - Top 20 Players")
        print("=" * 80)
        detailed_top = scored_df.nlargest(20, 'overall_score')[['full_name', 'team_name', 'position', 
                                                               'overall_score', 'batting_score', 
                                                               'pitching_score', 'fielding_score']]
        
        print(f"{'Name':20s} {'Team':15s} {'Pos':12s} {'Overall':>7s} {'Batting':>7s} {'Pitching':>8s} {'Fielding':>8s}")
        print("-" * 80)
        
        for idx, player in detailed_top.iterrows():
            print(f"{player['full_name'][:19]:20s} "
                  f"{player['team_name'][:14]:15s} "
                  f"{player['position'][:11]:12s} "
                  f"{player['overall_score']:7.1f} "
                  f"{player['batting_score']:7.1f} "
                  f"{player['pitching_score']:8.1f} "
                  f"{player['fielding_score']:8.1f}")
        
        # Component leaders
        print(f"\n🎯 COMPONENT LEADERS:")
        print("-" * 30)
        
        batting_leader = scored_df.loc[scored_df['batting_score'].idxmax()]
        pitching_leader = scored_df.loc[scored_df['pitching_score'].idxmax()]
        fielding_leader = scored_df.loc[scored_df['fielding_score'].idxmax()]
        
        print(f"Best Batting:  {batting_leader['full_name']:20s} | {batting_leader['batting_score']:5.1f} | {batting_leader['team_name']} ({batting_leader['position']})")
        print(f"Best Pitching: {pitching_leader['full_name']:20s} | {pitching_leader['pitching_score']:5.1f} | {pitching_leader['team_name']} ({pitching_leader['position']})")
        print(f"Best Fielding: {fielding_leader['full_name']:20s} | {fielding_leader['fielding_score']:5.1f} | {fielding_leader['team_name']} ({fielding_leader['position']})")
        
        # Position breakdowns
        print(f"\n📍 BEST PLAYERS BY POSITION:")
        print("-" * 35)
        position_leaders = scored_df.loc[scored_df.groupby('position')['overall_score'].idxmax()]
        position_leaders = position_leaders.sort_values('overall_score', ascending=False)
        
        for _, player in position_leaders.head(15).iterrows():
            print(f"{player['position']:15s}: {player['overall_score']:5.1f} | {player['full_name']:20s} | {player['team_name']}")
            if show_all_scores:
                print(f"{'':15s}  Batting: {player['batting_score']:4.1f} | Pitching: {player['pitching_score']:4.1f} | Fielding: {player['fielding_score']:4.1f}")
    
    # Best by position (summary)
    else:
        print(f"\n🎯 Best Player by Position:")
        position_leaders = scored_df.loc[scored_df.groupby('position')['overall_score'].idxmax()]
        position_leaders = position_leaders.sort_values('overall_score', ascending=False)
        
        for _, player in position_leaders.head(10).iterrows():
            print(f"  {player['position']:15s}: {player['overall_score']:5.1f} | {player['full_name']} ({player['team_name']})")
    
    # Score distribution by component
    print(f"\n📊 Score Distribution by Component:")
    components = ['batting_score', 'pitching_score', 'fielding_score', 'overall_score']
    for component in components:
        if component in scored_df.columns:
            avg_score = scored_df[component].mean()
            std_score = scored_df[component].std()
            print(f"  {component:15s}: {avg_score:5.2f} average (±{std_score:4.2f} std dev)")
    
    if show_all_scores:
        # Team averages
        print(f"\n🏟️ TEAM AVERAGES (Top 10):")
        print("-" * 25)
        team_averages = scored_df.groupby('team_name').agg({
            'overall_score': 'mean',
            'batting_score': 'mean', 
            'pitching_score': 'mean',
            'fielding_score': 'mean'
        }).round(1).sort_values('overall_score', ascending=False)
        
        print(f"{'Team':20s} {'Overall':>7s} {'Batting':>7s} {'Pitching':>8s} {'Fielding':>8s}")
        print("-" * 55)
        
        for team, scores in team_averages.head(10).iterrows():
            print(f"{team[:19]:20s} "
                  f"{scores['overall_score']:7.1f} "
                  f"{scores['batting_score']:7.1f} "
                  f"{scores['pitching_score']:8.1f} "
                  f"{scores['fielding_score']:8.1f}")

def main():
    parser = argparse.ArgumentParser(description='Score MLB players based on statistics')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--output-dir', default='data/processed', help='Output directory')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze data quality, do not score')
    parser.add_argument('--show-scores', action='store_true', help='Show detailed score breakdowns for all components')
    
    args = parser.parse_args()
    
    print(f"🏈 MLB Player Scoring System - {args.season}")
    print("=" * 40)
    
    try:
        # Load player data
        players_df = load_player_data(args.data_dir, args.season)
        
        # Analyze data quality
        analyze_data_quality(players_df)
        
        if args.analyze_only:
            print("\n✅ Data analysis complete!")
            return
        
        # Initialize scorer
        print(f"\n⚡ Initializing player scorer...")
        scorer = PlayerScorer()
        
        # Score all players
        print(f"\n🎯 Scoring players...")
        scored_df = scorer.score_all_players(players_df)
        
        # Save results
        output_file = save_scored_data(scored_df, args.output_dir, args.season)
        
        # Generate summary report
        generate_summary_report(scored_df, args.season, args.show_scores)
        
        print(f"\n🎉 Player scoring completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        if not args.show_scores:
            print(f"\n💡 Tip: Use --show-scores for detailed component breakdowns")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure to run data collection first: python scripts/collect_data.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
