# src/features/player_scoring.py

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlayerScorer:
    """
    Advanced player scoring system that converts baseball statistics into comparable scores
    """
    
    def __init__(self):
        # Position-specific weights for different skills
        self.position_weights = {
            'Pitcher': {
                'pitching': 0.95,
                'batting': 0.05,
                'fielding': 0.0
            },
            'Catcher': {
                'pitching': 0.0,
                'batting': 0.40,
                'fielding': 0.60
            },
            'First Baseman': {
                'pitching': 0.0,
                'batting': 0.70,
                'fielding': 0.30
            },
            'Second Baseman': {
                'pitching': 0.0,
                'batting': 0.50,
                'fielding': 0.50
            },
            'Third Baseman': {
                'pitching': 0.0,
                'batting': 0.60,
                'fielding': 0.40
            },
            'Shortstop': {
                'pitching': 0.0,
                'batting': 0.45,
                'fielding': 0.55
            },
            'Left Fielder': {
                'pitching': 0.0,
                'batting': 0.75,
                'fielding': 0.25
            },
            'Center Fielder': {
                'pitching': 0.0,
                'batting': 0.65,
                'fielding': 0.35
            },
            'Right Fielder': {
                'pitching': 0.0,
                'batting': 0.75,
                'fielding': 0.25
            },
            'Designated Hitter': {
                'pitching': 0.0,
                'batting': 1.0,
                'fielding': 0.0
            },
            'Outfielder': {  # Generic outfielder
                'pitching': 0.0,
                'batting': 0.70,
                'fielding': 0.30
            }
        }
        
        # Default weights if position not found
        self.default_weights = {
            'pitching': 0.0,
            'batting': 0.60,
            'fielding': 0.40
        }
        
        # Statistical benchmarks for normalization (MLB averages/good performance)
        self.batting_benchmarks = {
            'avg': {'poor': 0.200, 'average': 0.260, 'good': 0.300, 'excellent': 0.350},
            'obp': {'poor': 0.280, 'average': 0.320, 'good': 0.360, 'excellent': 0.420},
            'slg': {'poor': 0.350, 'average': 0.420, 'good': 0.500, 'excellent': 0.600},
            'ops': {'poor': 0.630, 'average': 0.740, 'good': 0.860, 'excellent': 1.000},
            'homeRuns': {'poor': 5, 'average': 15, 'good': 25, 'excellent': 40},
            'rbi': {'poor': 30, 'average': 60, 'good': 90, 'excellent': 120},
            'runs': {'poor': 40, 'average': 70, 'good': 100, 'excellent': 130},
            'stolenBases': {'poor': 2, 'average': 8, 'good': 20, 'excellent': 40}
        }
        
        self.pitching_benchmarks = {
            'era': {'excellent': 2.50, 'good': 3.50, 'average': 4.20, 'poor': 5.50},  # Lower is better
            'whip': {'excellent': 1.00, 'good': 1.20, 'average': 1.35, 'poor': 1.60},  # Lower is better
            'strikeOuts': {'poor': 50, 'average': 120, 'good': 180, 'excellent': 250},
            'wins': {'poor': 5, 'average': 10, 'good': 15, 'excellent': 20},
            'saves': {'poor': 5, 'average': 20, 'good': 35, 'excellent': 45}
        }
        
        self.fielding_benchmarks = {
            'fieldingPercentage': {'poor': 0.950, 'average': 0.975, 'good': 0.985, 'excellent': 0.995},
            'errors': {'excellent': 2, 'good': 8, 'average': 15, 'poor': 25}  # Lower is better
        }
    
    def normalize_stat(self, value: float, benchmarks: Dict, reverse: bool = False) -> float:
        """
        Normalize a statistic to a 0-100 scale based on benchmarks
        
        Args:
            value: The statistic value
            benchmarks: Dictionary with 'poor', 'average', 'good', 'excellent' thresholds
            reverse: True for stats where lower is better (like ERA)
        """
        if pd.isna(value) or value is None:
            return 0.0
        
        if reverse:
            # For stats where lower is better (ERA, WHIP, errors)
            if value <= benchmarks['excellent']:
                return 100.0
            elif value <= benchmarks['good']:
                return 75.0 + 25.0 * (benchmarks['good'] - value) / (benchmarks['good'] - benchmarks['excellent'])
            elif value <= benchmarks['average']:
                return 50.0 + 25.0 * (benchmarks['average'] - value) / (benchmarks['average'] - benchmarks['good'])
            elif value <= benchmarks['poor']:
                return 25.0 + 25.0 * (benchmarks['poor'] - value) / (benchmarks['poor'] - benchmarks['average'])
            else:
                return max(0.0, 25.0 * (6.0 - value) / (6.0 - benchmarks['poor']))
        else:
            # For stats where higher is better
            if value >= benchmarks['excellent']:
                return 100.0
            elif value >= benchmarks['good']:
                return 75.0 + 25.0 * (value - benchmarks['good']) / (benchmarks['excellent'] - benchmarks['good'])
            elif value >= benchmarks['average']:
                return 50.0 + 25.0 * (value - benchmarks['average']) / (benchmarks['good'] - benchmarks['average'])
            elif value >= benchmarks['poor']:
                return 25.0 + 25.0 * (value - benchmarks['poor']) / (benchmarks['average'] - benchmarks['poor'])
            else:
                return max(0.0, 25.0 * value / benchmarks['poor'])
    
    def calculate_batting_score(self, player_stats: Dict) -> float:
        """Calculate batting performance score (0-100)"""
        if not player_stats:
            return 0.0
        
        # Core batting stats with weights
        batting_components = {
            'avg': 0.20,      # Batting average
            'obp': 0.25,      # On-base percentage
            'slg': 0.25,      # Slugging percentage
            'ops': 0.15,      # OPS (some overlap with OBP/SLG but important)
            'homeRuns': 0.10, # Power
            'rbi': 0.05       # Run production
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for stat, weight in batting_components.items():
            if stat in player_stats and player_stats[stat] is not None:
                normalized_score = self.normalize_stat(
                    player_stats[stat], 
                    self.batting_benchmarks[stat]
                )
                total_score += normalized_score * weight
                total_weight += weight
        
        # Handle case where some stats are missing
        if total_weight > 0:
            return total_score / total_weight
        return 0.0
    
    def calculate_pitching_score(self, player_stats: Dict) -> float:
        """Calculate pitching performance score (0-100)"""
        if not player_stats:
            return 0.0
        
        # Core pitching stats with weights
        pitching_components = {
            'era': 0.30,        # Earned Run Average (lower is better)
            'whip': 0.25,       # Walks + Hits per Inning Pitched (lower is better)
            'strikeOuts': 0.20, # Strikeouts
            'wins': 0.15,       # Wins (team dependent but still valuable)
            'saves': 0.10       # Saves (for closers)
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for stat, weight in pitching_components.items():
            if stat in player_stats and player_stats[stat] is not None:
                reverse = stat in ['era', 'whip']  # Lower is better for these
                normalized_score = self.normalize_stat(
                    player_stats[stat], 
                    self.pitching_benchmarks[stat],
                    reverse=reverse
                )
                total_score += normalized_score * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 0.0
    
    def calculate_fielding_score(self, player_stats: Dict) -> float:
        """Calculate fielding performance score (0-100)"""
        if not player_stats:
            return 50.0  # Default average fielding
        
        fielding_components = {
            'fieldingPercentage': 0.70,
            'errors': 0.30
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for stat, weight in fielding_components.items():
            if stat in player_stats and player_stats[stat] is not None:
                reverse = stat == 'errors'  # Lower errors is better
                normalized_score = self.normalize_stat(
                    player_stats[stat], 
                    self.fielding_benchmarks[stat],
                    reverse=reverse
                )
                total_score += normalized_score * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 50.0  # Default average fielding if no stats
    
    def get_position_weights(self, position: str) -> Dict[str, float]:
        """Get weights for a specific position"""
        # Clean up position name
        position = position.strip()
        
        # Direct match
        if position in self.position_weights:
            return self.position_weights[position]
        
        # Handle common variations
        position_mapping = {
            '1B': 'First Baseman',
            '2B': 'Second Baseman', 
            '3B': 'Third Baseman',
            'SS': 'Shortstop',
            'LF': 'Left Fielder',
            'CF': 'Center Fielder',
            'RF': 'Right Fielder',
            'C': 'Catcher',
            'P': 'Pitcher',
            'DH': 'Designated Hitter',
            'OF': 'Outfielder'
        }
        
        if position in position_mapping:
            return self.position_weights[position_mapping[position]]
        
        # Default weights for unknown positions
        return self.default_weights
    
    def calculate_player_score(self, player_stats: Dict, position: str = None) -> Dict[str, float]:
        """
        Calculate overall player score combining batting, pitching, and fielding
        
        Returns:
            Dictionary with individual component scores and overall score
        """
        # Calculate component scores
        batting_score = self.calculate_batting_score(player_stats)
        pitching_score = self.calculate_pitching_score(player_stats)
        fielding_score = self.calculate_fielding_score(player_stats)
        
        # Get position weights
        if position:
            weights = self.get_position_weights(position)
        else:
            weights = self.default_weights
        
        # Calculate weighted overall score
        overall_score = (
            batting_score * weights['batting'] +
            pitching_score * weights['pitching'] +
            fielding_score * weights['fielding']
        )
        
        return {
            'batting_score': round(batting_score, 2),
            'pitching_score': round(pitching_score, 2),
            'fielding_score': round(fielding_score, 2),
            'overall_score': round(overall_score, 2),
            'position': position,
            'weights_used': weights
        }
    
    def score_all_players(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Score all players in a DataFrame"""
        logger.info(f"Scoring {len(players_df)} players...")
        
        scores = []
        for idx, player in players_df.iterrows():
            # Convert player row to dictionary
            player_stats = player.to_dict()
            position = player.get('position', '')
            
            # Calculate scores
            score_result = self.calculate_player_score(player_stats, position)
            
            # Combine with original player data
            scored_player = {
                'player_id': player.get('player_id'),
                'full_name': player.get('full_name'),
                'team_name': player.get('team_name'),
                'position': position,
                **score_result
            }
            
            scores.append(scored_player)
        
        logger.info("Player scoring completed!")
        return pd.DataFrame(scores)


# Example usage and testing
if __name__ == "__main__":
    # Test the scoring system
    scorer = PlayerScorer()
    
    # Example player data
    test_players = [
        {
            'player_id': 1,
            'full_name': 'Test Batter',
            'position': 'First Baseman',
            'avg': 0.285,
            'obp': 0.350,
            'slg': 0.520,
            'ops': 0.870,
            'homeRuns': 28,
            'rbi': 85,
            'fieldingPercentage': 0.992,
            'errors': 5
        },
        {
            'player_id': 2,
            'full_name': 'Test Pitcher',
            'position': 'Pitcher',
            'era': 3.25,
            'whip': 1.15,
            'strikeOuts': 165,
            'wins': 12,
            'saves': 0,
            'avg': 0.125,  # Pitchers typically bat poorly
            'fieldingPercentage': 0.985
        }
    ]
    
    for player in test_players:
        scores = scorer.calculate_player_score(player, player['position'])
        print(f"\n{player['full_name']} ({player['position']})")
        print(f"  Batting: {scores['batting_score']}")
        print(f"  Pitching: {scores['pitching_score']}")
        print(f"  Fielding: {scores['fielding_score']}")
        print(f"  Overall: {scores['overall_score']}")
