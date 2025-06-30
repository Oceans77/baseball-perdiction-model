# src/features/team_scoring.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamScorer:
    """
    Team scoring system that aggregates individual player scores into team strength ratings
    """
    
    def __init__(self):
        # Position importance weights for team composition
        self.position_importance = {
            'Pitcher': 0.35,        # Pitching is crucial
            'Catcher': 0.08,        # Important for game management
            'First Baseman': 0.07,  # Offensive position
            'Second Baseman': 0.06, # Balanced importance
            'Third Baseman': 0.07,  # Power position
            'Shortstop': 0.08,      # Key defensive position
            'Left Fielder': 0.06,   # Outfield positions
            'Center Fielder': 0.08, # Most important outfield position
            'Right Fielder': 0.06,  # Outfield positions
            'Designated Hitter': 0.05, # Offensive specialist
            'Outfielder': 0.06      # Generic outfielder
        }
        
        # Minimum number of players needed per position for a complete team
        self.position_requirements = {
            'Pitcher': 5,           # Starting rotation + relievers
            'Catcher': 2,           # Primary + backup
            'First Baseman': 1,     # Primary
            'Second Baseman': 1,    # Primary
            'Third Baseman': 1,     # Primary
            'Shortstop': 1,         # Primary
            'Left Fielder': 1,      # Primary
            'Center Fielder': 1,    # Primary
            'Right Fielder': 1,     # Primary
            'Designated Hitter': 1  # Primary
        }
    
    def aggregate_player_scores_by_position(self, team_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Aggregate player scores by position for a team
        
        Returns:
            Dictionary with position-level aggregated scores
        """
        position_scores = {}
        
        for position in team_df['position'].unique():
            if pd.isna(position) or position == '':
                continue
                
            position_players = team_df[team_df['position'] == position]
            
            # Calculate various aggregation methods
            position_scores[position] = {
                'player_count': len(position_players),
                'avg_overall_score': position_players['overall_score'].mean(),
                'max_overall_score': position_players['overall_score'].max(),
                'min_overall_score': position_players['overall_score'].min(),
                'top_3_avg': position_players.nlargest(3, 'overall_score')['overall_score'].mean(),
                'depth_score': self.calculate_position_depth_score(position_players),
                'avg_batting_score': position_players['batting_score'].mean(),
                'avg_pitching_score': position_players['pitching_score'].mean(),
                'avg_fielding_score': position_players['fielding_score'].mean(),
                'players': position_players[['full_name', 'overall_score']].to_dict('records')
            }
        
        return position_scores
    
    def calculate_position_depth_score(self, position_players: pd.DataFrame) -> float:
        """
        Calculate depth score for a position based on quality of bench players
        """
        if len(position_players) == 0:
            return 0.0
        
        # Sort by overall score descending
        sorted_players = position_players.sort_values('overall_score', ascending=False)
        
        if len(sorted_players) == 1:
            # No depth, just the starter
            return sorted_players.iloc[0]['overall_score'] * 0.8  # Penalty for no depth
        elif len(sorted_players) == 2:
            # Starter + 1 backup
            starter_score = sorted_players.iloc[0]['overall_score']
            backup_score = sorted_players.iloc[1]['overall_score']
            return starter_score * 0.7 + backup_score * 0.3
        else:
            # Good depth
            starter_score = sorted_players.iloc[0]['overall_score']
            backup_scores = sorted_players.iloc[1:3]['overall_score'].mean()  # Top 2 backups
            return starter_score * 0.6 + backup_scores * 0.4
    
    def calculate_team_score(self, team_df: pd.DataFrame, team_name: str) -> Dict:
        """
        Calculate comprehensive team score
        
        Args:
            team_df: DataFrame with scored players for a single team
            team_name: Name of the team
            
        Returns:
            Dictionary with team scores and breakdown
        """
        if len(team_df) == 0:
            return {
                'team_name': team_name,
                'overall_score': 0.0,
                'error': 'No players found'
            }
        
        # Get position-level scores
        position_scores = self.aggregate_player_scores_by_position(team_df)
        
        # Calculate weighted team score
        total_weighted_score = 0.0
        total_weight = 0.0
        position_breakdown = {}
        
        for position, importance in self.position_importance.items():
            if position in position_scores:
                # Use depth score as the position's contribution
                position_contribution = position_scores[position]['depth_score']
                total_weighted_score += position_contribution * importance
                total_weight += importance
                
                position_breakdown[position] = {
                    'score': position_contribution,
                    'weight': importance,
                    'player_count': position_scores[position]['player_count'],
                    'contribution': position_contribution * importance
                }
            else:
                # Missing position - significant penalty
                position_breakdown[position] = {
                    'score': 0.0,
                    'weight': importance,
                    'player_count': 0,
                    'contribution': 0.0,
                    'missing': True
                }
        
        # Calculate final team score
        if total_weight > 0:
            team_overall_score = total_weighted_score / total_weight
        else:
            team_overall_score = 0.0
        
        # Calculate component scores (batting, pitching, fielding)
        team_batting_score = team_df['batting_score'].mean()
        team_pitching_score = team_df['pitching_score'].mean()
        team_fielding_score = team_df['fielding_score'].mean()
        
        # Calculate roster completeness penalty
        completeness_penalty = self.calculate_roster_completeness_penalty(position_scores)
        adjusted_team_score = team_overall_score * (1 - completeness_penalty)
        
        return {
            'team_name': team_name,
            'overall_score': round(adjusted_team_score, 2),
            'raw_score': round(team_overall_score, 2),
            'batting_score': round(team_batting_score, 2),
            'pitching_score': round(team_pitching_score, 2),
            'fielding_score': round(team_fielding_score, 2),
            'roster_size': len(team_df),
            'completeness_penalty': round(completeness_penalty, 3),
            'position_breakdown': position_breakdown,
            'top_players': team_df.nlargest(5, 'overall_score')[['full_name', 'position', 'overall_score']].to_dict('records')
        }
    
    def calculate_roster_completeness_penalty(self, position_scores: Dict) -> float:
        """
        Calculate penalty for incomplete roster
        """
        penalty = 0.0
        
        for position, min_required in self.position_requirements.items():
            if position not in position_scores:
                # Missing entire position
                penalty += self.position_importance.get(position, 0.05) * 0.5
            elif position_scores[position]['player_count'] < min_required:
                # Insufficient depth
                shortage = min_required - position_scores[position]['player_count']
                penalty += self.position_importance.get(position, 0.05) * 0.2 * shortage
        
        return min(penalty, 0.3)  # Cap penalty at 30%
    
    def score_all_teams(self, scored_players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Score all teams based on their players
        
        Args:
            scored_players_df: DataFrame with all scored players
            
        Returns:
            DataFrame with team scores
        """
        logger.info(f"Calculating team scores for {scored_players_df['team_name'].nunique()} teams...")
        
        team_scores = []
        
        for team_name in scored_players_df['team_name'].unique():
            if pd.isna(team_name):
                continue
                
            logger.info(f"Scoring team: {team_name}")
            
            # Get players for this team
            team_players = scored_players_df[scored_players_df['team_name'] == team_name]
            
            # Calculate team score
            team_score = self.calculate_team_score(team_players, team_name)
            team_scores.append(team_score)
        
        # Convert to DataFrame and sort by overall score
        team_scores_df = pd.DataFrame(team_scores)
        team_scores_df = team_scores_df.sort_values('overall_score', ascending=False)
        
        logger.info("Team scoring completed!")
        return team_scores_df
    
    def generate_matchup_prediction(self, team1_score: Dict, team2_score: Dict) -> Dict:
        """
        Generate a prediction for a matchup between two teams
        
        Args:
            team1_score: Team 1 scoring data
            team2_score: Team 2 scoring data
            
        Returns:
            Dictionary with prediction details
        """
        team1_overall = team1_score['overall_score']
        team2_overall = team2_score['overall_score']
        
        # Calculate win probability using logistic function
        score_difference = team1_overall - team2_overall
        
        # Convert score difference to probability (sigmoid function)
        win_probability_team1 = 1 / (1 + np.exp(-score_difference / 10))  # Scaling factor of 10
        win_probability_team2 = 1 - win_probability_team1
        
        # Determine predicted winner
        if win_probability_team1 > 0.5:
            predicted_winner = team1_score['team_name']
            confidence = win_probability_team1
        else:
            predicted_winner = team2_score['team_name']
            confidence = win_probability_team2
        
        # Calculate component advantages
        batting_advantage = team1_score['batting_score'] - team2_score['batting_score']
        pitching_advantage = team1_score['pitching_score'] - team2_score['pitching_score']
        fielding_advantage = team1_score['fielding_score'] - team2_score['fielding_score']
        
        return {
            'team1': team1_score['team_name'],
            'team2': team2_score['team_name'],
            'team1_score': team1_overall,
            'team2_score': team2_overall,
            'predicted_winner': predicted_winner,
            'win_probability': round(confidence, 3),
            'score_difference': round(abs(score_difference), 2),
            'advantages': {
                'batting': {
                    'leader': team1_score['team_name'] if batting_advantage > 0 else team2_score['team_name'],
                    'advantage': round(abs(batting_advantage), 2)
                },
                'pitching': {
                    'leader': team1_score['team_name'] if pitching_advantage > 0 else team2_score['team_name'],
                    'advantage': round(abs(pitching_advantage), 2)
                },
                'fielding': {
                    'leader': team1_score['team_name'] if fielding_advantage > 0 else team2_score['team_name'],
                    'advantage': round(abs(fielding_advantage), 2)
                }
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the team scoring system
    team_scorer = TeamScorer()
    
    # Example scored players data
    test_data = [
        {'full_name': 'Player 1', 'team_name': 'Team A', 'position': 'Pitcher', 'overall_score': 85, 'batting_score': 30, 'pitching_score': 95, 'fielding_score': 80},
        {'full_name': 'Player 2', 'team_name': 'Team A', 'position': 'Catcher', 'overall_score': 70, 'batting_score': 65, 'pitching_score': 0, 'fielding_score': 85},
        {'full_name': 'Player 3', 'team_name': 'Team A', 'position': 'First Baseman', 'overall_score': 78, 'batting_score': 80, 'pitching_score': 0, 'fielding_score': 75},
        {'full_name': 'Player 4', 'team_name': 'Team B', 'position': 'Pitcher', 'overall_score': 82, 'batting_score': 25, 'pitching_score': 90, 'fielding_score': 78},
        {'full_name': 'Player 5', 'team_name': 'Team B', 'position': 'Catcher', 'overall_score': 68, 'batting_score': 62, 'pitching_score': 0, 'fielding_score': 82},
    ]
    
    test_df = pd.DataFrame(test_data)
    
    # Score teams
    team_scores = team_scorer.score_all_teams(test_df)
    print("Team Scores:")
    print(team_scores[['team_name', 'overall_score', 'batting_score', 'pitching_score', 'fielding_score']])
    
    # Test matchup prediction
    if len(team_scores) >= 2:
        team1_data = team_scores.iloc[0].to_dict()
        team2_data = team_scores.iloc[1].to_dict()
        
        prediction = team_scorer.generate_matchup_prediction(team1_data, team2_data)
        print(f"\nMatchup Prediction:")
        print(f"{prediction['team1']} vs {prediction['team2']}")
        print(f"Predicted Winner: {prediction['predicted_winner']} ({prediction['win_probability']:.1%} confidence)")
        print(f"Score Difference: {prediction['score_difference']}")
