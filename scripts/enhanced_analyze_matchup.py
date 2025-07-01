#!/usr/bin/env python3
"""
Enhanced Team Matchup Analyzer with Weather and Betting Data Integration
Usage: python scripts/enhanced_analyze_matchup.py "Team A" "Team B" [--detailed] [--weather] [--betting]

Save this file as: scripts/enhanced_analyze_matchup.py
"""

import sys
import os
import argparse
import pandas as pd
import json
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.team_scoring import TeamScorer

class WeatherService:
    """
    Service to fetch weather data that affects baseball games
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # MLB stadium locations (lat, lon)
        self.stadium_locations = {
            "Arizona Diamondbacks": (33.4455, -112.0667),
            "Atlanta Braves": (33.8906, -84.4677),
            "Baltimore Orioles": (39.2838, -76.6216),
            "Boston Red Sox": (42.3467, -71.0972),
            "Chicago Cubs": (41.9484, -87.6553),
            "Chicago White Sox": (41.8299, -87.6338),
            "Cincinnati Reds": (39.0975, -84.5061),
            "Cleveland Guardians": (41.4962, -81.6852),
            "Colorado Rockies": (39.7559, -104.9942),
            "Detroit Tigers": (42.3391, -83.0485),
            "Houston Astros": (29.7572, -95.3555),
            "Kansas City Royals": (39.0517, -94.4803),
            "Los Angeles Angels": (33.8003, -117.8827),
            "Los Angeles Dodgers": (34.0739, -118.2400),
            "Miami Marlins": (25.7781, -80.2196),
            "Milwaukee Brewers": (43.0280, -87.9712),
            "Minnesota Twins": (44.9817, -93.2776),
            "New York Mets": (40.7571, -73.8458),
            "New York Yankees": (40.8296, -73.9262),
            "Oakland Athletics": (37.7516, -122.2005),
            "Philadelphia Phillies": (39.9061, -75.1665),
            "Pittsburgh Pirates": (40.4469, -80.0056),
            "San Diego Padres": (32.7073, -117.1566),
            "San Francisco Giants": (37.7786, -122.3893),
            "Seattle Mariners": (47.5914, -122.3326),
            "St. Louis Cardinals": (38.6226, -90.1928),
            "Tampa Bay Rays": (27.7682, -82.6534),
            "Texas Rangers": (32.7513, -97.0834),
            "Toronto Blue Jays": (43.6414, -79.3894),
            "Washington Nationals": (38.8730, -77.0074)
        }
    
    def get_weather_data(self, team_name: str, game_date: str = None) -> Dict:
        """
        Get weather data for a team's stadium
        """
        if not self.api_key:
            return self._get_mock_weather_data(team_name)
        
        if team_name not in self.stadium_locations:
            return {"error": f"Stadium location not found for {team_name}"}
        
        lat, lon = self.stadium_locations[team_name]
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "imperial"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._process_weather_data(data, team_name)
            
        except Exception as e:
            print(f"⚠️  Weather API error: {e}")
            return self._get_mock_weather_data(team_name)
    
    def _process_weather_data(self, weather_data: Dict, team_name: str) -> Dict:
        """Process raw weather data into game impact factors"""
        
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind'].get('speed', 0)
        wind_direction = weather_data['wind'].get('deg', 0)
        pressure = weather_data['main']['pressure']
        conditions = weather_data['weather'][0]['main'].lower()
        
        # Calculate baseball-specific impacts
        pitching_impact = self._calculate_pitching_weather_impact(temp, humidity, pressure, conditions)
        batting_impact = self._calculate_batting_weather_impact(temp, wind_speed, wind_direction, conditions)
        
        return {
            "team_name": team_name,
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "pressure": pressure,
            "conditions": conditions,
            "description": weather_data['weather'][0]['description'],
            "pitching_impact": pitching_impact,
            "batting_impact": batting_impact,
            "overall_impact": (pitching_impact + batting_impact) / 2,
            "weather_summary": self._generate_weather_summary(temp, wind_speed, conditions, pitching_impact, batting_impact)
        }
    
    def _calculate_pitching_weather_impact(self, temp: float, humidity: float, pressure: float, conditions: str) -> float:
        """Calculate how weather affects pitching performance"""
        impact = 0.0
        
        # Temperature effects
        if 65 <= temp <= 75:
            impact += 0.2  # Ideal pitching temperature
        elif temp < 50 or temp > 85:
            impact -= 0.3  # Extreme temperatures hurt pitching
        
        # Humidity effects
        if humidity > 80:
            impact += 0.1  # Helps breaking balls
        elif humidity < 40:
            impact -= 0.1  # Dry air, less ball movement
        
        # Pressure effects
        if pressure < 29.80:
            impact -= 0.2  # Low pressure favors hitters
        elif pressure > 30.20:
            impact += 0.1  # High pressure favors pitchers
        
        # Weather conditions
        if conditions in ['rain', 'drizzle', 'thunderstorm']:
            impact -= 0.4  # Poor conditions for pitchers
        elif conditions == 'clear':
            impact += 0.1  # Clear weather is good for pitching
        
        return max(-1.0, min(1.0, impact))
    
    def _calculate_batting_weather_impact(self, temp: float, wind_speed: float, wind_direction: float, conditions: str) -> float:
        """Calculate how weather affects batting performance"""
        impact = 0.0
        
        # Temperature effects
        if temp > 80:
            impact += 0.3  # Hot weather helps hitters
        elif temp < 50:
            impact -= 0.2  # Cold weather hurts hitters
        elif 70 <= temp <= 80:
            impact += 0.1  # Good hitting weather
        
        # Wind effects
        if wind_speed > 15:
            impact -= 0.2  # Strong wind generally hurts hitters
        elif 5 <= wind_speed <= 10:
            if 90 <= wind_direction <= 270:  # Roughly blowing out
                impact += 0.2
            else:
                impact -= 0.1
        
        # Weather conditions
        if conditions in ['rain', 'drizzle']:
            impact -= 0.3  # Poor hitting conditions
        elif conditions == 'clear':
            impact += 0.1  # Clear weather helps hitters
        
        return max(-1.0, min(1.0, impact))
    
    def _generate_weather_summary(self, temp: float, wind_speed: float, conditions: str, pitching_impact: float, batting_impact: float) -> str:
        """Generate human-readable weather summary"""
        summary_parts = []
        
        if temp > 80:
            summary_parts.append(f"Hot weather ({temp:.0f}°F) favors hitters")
        elif temp < 50:
            summary_parts.append(f"Cold weather ({temp:.0f}°F) favors pitchers")
        else:
            summary_parts.append(f"Moderate temperature ({temp:.0f}°F)")
        
        if wind_speed > 15:
            summary_parts.append(f"Strong winds ({wind_speed:.0f} mph) may affect play")
        elif wind_speed > 10:
            summary_parts.append(f"Moderate winds ({wind_speed:.0f} mph)")
        
        if conditions in ['rain', 'drizzle', 'thunderstorm']:
            summary_parts.append("Poor weather conditions expected")
        
        if pitching_impact > 0.2:
            summary_parts.append("Weather favors pitchers")
        elif batting_impact > 0.2:
            summary_parts.append("Weather favors hitters")
        
        return "; ".join(summary_parts) if summary_parts else "Neutral weather conditions"
    
    def _get_mock_weather_data(self, team_name: str) -> Dict:
        """Generate mock weather data for testing"""
        import random
        
        mock_temp = random.uniform(60, 85)
        mock_wind = random.uniform(3, 12)
        mock_humidity = random.uniform(45, 75)
        
        conditions = random.choice(['clear', 'partly cloudy', 'cloudy'])
        
        pitching_impact = self._calculate_pitching_weather_impact(mock_temp, mock_humidity, 30.0, conditions)
        batting_impact = self._calculate_batting_weather_impact(mock_temp, mock_wind, 180, conditions)
        
        return {
            "team_name": team_name,
            "temperature": mock_temp,
            "humidity": mock_humidity,
            "wind_speed": mock_wind,
            "wind_direction": 180,
            "pressure": 30.0,
            "conditions": conditions,
            "description": f"Mock {conditions} weather",
            "pitching_impact": pitching_impact,
            "batting_impact": batting_impact,
            "overall_impact": (pitching_impact + batting_impact) / 2,
            "weather_summary": f"Mock weather: {mock_temp:.0f}°F, {mock_wind:.0f} mph winds",
            "mock_data": True
        }


class BettingDataService:
    """
    Service to fetch betting odds and predictions from various sources
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.sources = []
        
    def get_betting_data(self, team1: str, team2: str) -> Dict:
        """Get betting odds and predictions for a matchup"""
        if not self.api_key:
            return self._get_mock_betting_data(team1, team2)
        
        # In a real implementation, you would call betting APIs here
        return self._get_mock_betting_data(team1, team2)
    
    def _get_mock_betting_data(self, team1: str, team2: str) -> Dict:
        """Generate realistic mock betting data"""
        import random
        
        # Generate realistic odds
        team1_odds = random.uniform(-200, 200)
        team2_odds = -team1_odds + random.uniform(-50, 50)
        
        # Convert odds to implied probability
        def odds_to_probability(odds):
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        team1_prob = odds_to_probability(team1_odds)
        team2_prob = odds_to_probability(team2_odds)
        
        # Normalize probabilities
        total_prob = team1_prob + team2_prob
        team1_prob = team1_prob / total_prob
        team2_prob = team2_prob / total_prob
        
        # Generate consensus data
        expert_picks = {
            team1: random.randint(3, 8),
            team2: random.randint(2, 7)
        }
        
        public_betting = {
            team1: random.uniform(0.3, 0.7),
            team2: 1 - random.uniform(0.3, 0.7)
        }
        
        return {
            "matchup": f"{team1} vs {team2}",
            "moneyline_odds": {
                team1: team1_odds,
                team2: team2_odds
            },
            "implied_probabilities": {
                team1: team1_prob,
                team2: team2_prob
            },
            "expert_consensus": expert_picks,
            "public_betting_percentage": public_betting,
            "run_line": {
                "favorite": team1 if team1_odds < team2_odds else team2,
                "spread": random.uniform(1.0, 2.5),
                "odds": random.uniform(-120, 120)
            },
            "over_under": {
                "total": random.uniform(7.5, 11.5),
                "over_odds": random.uniform(-115, 115),
                "under_odds": random.uniform(-115, 115)
            },
            "betting_summary": self._generate_betting_summary(team1, team2, team1_prob, expert_picks, public_betting),
            "mock_data": True
        }
    
    def _generate_betting_summary(self, team1: str, team2: str, team1_prob: float, expert_picks: Dict, public_betting: Dict) -> str:
        """Generate betting summary"""
        favorite = team1 if team1_prob > 0.5 else team2
        prob = max(team1_prob, 1 - team1_prob)
        
        expert_favorite = max(expert_picks, key=expert_picks.get)
        public_favorite = max(public_betting, key=public_betting.get)
        
        summary = f"Vegas favorite: {favorite} ({prob:.1%})"
        if expert_favorite == public_favorite == favorite:
            summary += f"; Consensus agrees with {favorite}"
        else:
            summary += f"; Mixed opinions - experts lean {expert_favorite}, public backs {public_favorite}"
        
        return summary


class EnhancedMatchupAnalyzer:
    """
    Enhanced matchup analyzer with weather and betting data integration
    """
    
    def __init__(self, data_dir: str = "data/processed", weather_api_key: str = None, betting_api_key: str = None):
        self.data_dir = data_dir
        self.team_scorer = TeamScorer()
        self.weather_service = WeatherService(weather_api_key)
        self.betting_service = BettingDataService(betting_api_key)
        
    def analyze_enhanced_matchup(self, team1_name: str, team2_name: str, season: int = 2024, 
                               include_weather: bool = True, include_betting: bool = True) -> Dict:
        """Generate enhanced matchup analysis with weather and betting data"""
        # Load basic team data
        players_df, teams_df, detailed_df = self._load_team_data(season)
        
        # Find teams
        team1 = self._find_team(team1_name, teams_df)
        team2 = self._find_team(team2_name, teams_df)
        
        if team1 is None:
            return {'error': f'Team "{team1_name}" not found'}
        if team2 is None:
            return {'error': f'Team "{team2_name}" not found'}
        
        # Generate basic prediction
        basic_prediction = self.team_scorer.generate_matchup_prediction(
            team1.to_dict(), team2.to_dict()
        )
        
        analysis = {
            'matchup_info': {
                'team1': team1['team_name'],
                'team2': team2['team_name'],
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'season': season
            },
            'basic_prediction': basic_prediction,
            'team_stats': {
                'team1': {
                    'overall_score': team1['overall_score'],
                    'batting_score': team1['batting_score'],
                    'pitching_score': team1['pitching_score'],
                    'fielding_score': team1['fielding_score']
                },
                'team2': {
                    'overall_score': team2['overall_score'],
                    'batting_score': team2['batting_score'],
                    'pitching_score': team2['pitching_score'],
                    'fielding_score': team2['fielding_score']
                }
            }
        }
        
        # Add weather analysis
        if include_weather:
            analysis['weather_analysis'] = self._analyze_weather_impact(team1['team_name'], team2['team_name'])
        
        # Add betting analysis
        if include_betting:
            analysis['betting_analysis'] = self._analyze_betting_data(team1['team_name'], team2['team_name'])
        
        # Generate enhanced prediction
        analysis['enhanced_prediction'] = self._generate_enhanced_prediction(analysis)
        
        return analysis
    
    def _analyze_weather_impact(self, team1_name: str, team2_name: str) -> Dict:
        """Analyze weather impact for both teams"""
        weather_data = self.weather_service.get_weather_data(team1_name)
        
        team1_weather_impact = self._calculate_team_weather_impact(team1_name, weather_data)
        team2_weather_impact = self._calculate_team_weather_impact(team2_name, weather_data)
        
        return {
            'location': f"{team1_name} (Home)",
            'weather_data': weather_data,
            'team_impacts': {
                team1_name: team1_weather_impact,
                team2_name: team2_weather_impact
            },
            'net_advantage': {
                'team': team1_name if team1_weather_impact > team2_weather_impact else team2_name,
                'advantage': abs(team1_weather_impact - team2_weather_impact)
            }
        }
    
    def _calculate_team_weather_impact(self, team_name: str, weather_data: Dict) -> float:
        """Calculate how weather specifically impacts this team"""
        pitching_impact = weather_data.get('pitching_impact', 0)
        batting_impact = weather_data.get('batting_impact', 0)
        return (pitching_impact + batting_impact) / 2
    
    def _analyze_betting_data(self, team1_name: str, team2_name: str) -> Dict:
        """Analyze betting data and expert predictions"""
        betting_data = self.betting_service.get_betting_data(team1_name, team2_name)
        
        team1_betting_prob = betting_data['implied_probabilities'][team1_name]
        team2_betting_prob = betting_data['implied_probabilities'][team2_name]
        
        return {
            'betting_data': betting_data,
            'vegas_favorite': team1_name if team1_betting_prob > 0.5 else team2_name,
            'vegas_confidence': max(team1_betting_prob, team2_betting_prob),
            'market_analysis': self._generate_market_analysis(betting_data)
        }
    
    def _generate_market_analysis(self, betting_data: Dict) -> str:
        """Generate analysis of betting market sentiment"""
        expert_picks = betting_data['expert_consensus']
        public_betting = betting_data['public_betting_percentage']
        
        expert_favorite = max(expert_picks, key=expert_picks.get)
        public_favorite = max(public_betting, key=public_betting.get)
        
        if expert_favorite == public_favorite:
            return f"Strong consensus backing {expert_favorite}"
        else:
            return f"Experts favor {expert_favorite}, but public backing {public_favorite} - potential value play"
    
    def _generate_enhanced_prediction(self, analysis: Dict) -> Dict:
        """Generate final prediction incorporating all factors"""
        basic_pred = analysis['basic_prediction']
        
        # Start with basic model prediction
        team1_prob = basic_pred['win_probability'] if basic_pred['predicted_winner'] == analysis['matchup_info']['team1'] else 1 - basic_pred['win_probability']
        
        # Adjust for weather if available
        if 'weather_analysis' in analysis:
            weather_impact = analysis['weather_analysis']['net_advantage']['advantage']
            weather_team = analysis['weather_analysis']['net_advantage']['team']
            
            if weather_team == analysis['matchup_info']['team1']:
                team1_prob += weather_impact * 0.05
            else:
                team1_prob -= weather_impact * 0.05
        
        # Adjust for betting data if available
        if 'betting_analysis' in analysis:
            vegas_prob = analysis['betting_analysis']['betting_data']['implied_probabilities'][analysis['matchup_info']['team1']]
            team1_prob = 0.7 * team1_prob + 0.3 * vegas_prob
        
        # Ensure probability stays in valid range
        team1_prob = max(0.05, min(0.95, team1_prob))
        team2_prob = 1 - team1_prob
        
        # Determine final winner
        final_winner = analysis['matchup_info']['team1'] if team1_prob > 0.5 else analysis['matchup_info']['team2']
        final_confidence = max(team1_prob, team2_prob)
        
        return {
            'final_winner': final_winner,
            'final_win_probability': round(final_confidence, 3),
            'team1_probability': round(team1_prob, 3),
            'team2_probability': round(team2_prob, 3),
            'confidence_level': 'High' if final_confidence > 0.65 else 'Medium' if final_confidence > 0.55 else 'Low',
            'prediction_factors': {
                'team_performance': basic_pred['win_probability'],
                'weather_adjustment': analysis.get('weather_analysis', {}).get('net_advantage', {}).get('advantage', 0),
                'betting_market_input': analysis.get('betting_analysis', {}).get('vegas_confidence', 0)
            }
        }
    
    def _load_team_data(self, season: int = 2024) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
    
    def _find_team(self, team_name: str, teams_df: pd.DataFrame) -> Optional[pd.Series]:
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


def print_enhanced_analysis(analysis: Dict, detailed: bool = False):
    """Print comprehensive enhanced matchup analysis"""
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    info = analysis['matchup_info']
    basic_pred = analysis['basic_prediction']
    enhanced_pred = analysis['enhanced_prediction']
    
    print(f"\n{'='*80}")
    print(f"🏟️  ENHANCED MLB MATCHUP ANALYSIS")
    print(f"{'='*80}")
    print(f"📅 Analysis Date: {info['analysis_date']}")
    print(f"🆚 Matchup: {info['team1']} vs {info['team2']}")
    print(f"📊 Season: {info['season']}")
    
    # Enhanced Prediction
    print(f"\n🎯 ENHANCED PREDICTION")
    print("─" * 30)
    print(f"🏆 Predicted Winner: {enhanced_pred['final_winner']}")
    print(f"📈 Win Probability: {enhanced_pred['final_win_probability']:.1%}")
    print(f"🎚️  Confidence Level: {enhanced_pred['confidence_level']}")
    print(f"📋 Breakdown:")
    print(f"   • {info['team1']}: {enhanced_pred['team1_probability']:.1%}")
    print(f"   • {info['team2']}: {enhanced_pred['team2_probability']:.1%}")
    
    # Team Performance Comparison
    print(f"\n⚔️  TEAM PERFORMANCE COMPARISON")
    print("─" * 40)
    team1_stats = analysis['team_stats']['team1']
    team2_stats = analysis['team_stats']['team2']
    
    print(f"{'Component':<15} {'Team1':<15} {'Team2':<15} {'Advantage':<20}")
    print("─" * 65)
    
    components = ['overall_score', 'batting_score', 'pitching_score', 'fielding_score']
    for comp in components:
        val1 = team1_stats[comp]
        val2 = team2_stats[comp]
        advantage = f"{info['team1'] if val1 > val2 else info['team2']} (+{abs(val1-val2):.1f})"
        comp_name = comp.replace('_', ' ').title()
        print(f"{comp_name:<15} {val1:<15.1f} {val2:<15.1f} {advantage:<20}")
    
    # Weather Analysis
    if 'weather_analysis' in analysis:
        weather = analysis['weather_analysis']
        weather_data = weather['weather_data']
        
        print(f"\n🌤️  WEATHER ANALYSIS")
        print("─" * 25)
        print(f"🏟️  Location: {weather['location']}")
        print(f"🌡️  Temperature: {weather_data['temperature']:.0f}°F")
        print(f"💨 Wind: {weather_data['wind_speed']:.0f} mph")
        print(f"💧 Humidity: {weather_data['humidity']:.0f}%")
        print(f"☁️  Conditions: {weather_data['description'].title()}")
        print(f"📊 Impact Summary: {weather_data['weather_summary']}")
        
        if detailed:
            print(f"\n📈 Detailed Weather Impacts:")
            print(f"   • Pitching Impact: {weather_data['pitching_impact']:+.2f}")
            print(f"   • Batting Impact: {weather_data['batting_impact']:+.2f}")
            print(f"   • Net Advantage: {weather['net_advantage']['team']} (+{weather['net_advantage']['advantage']:.2f})")
    
    # Betting Analysis
    if 'betting_analysis' in analysis:
        betting = analysis['betting_analysis']
        betting_data = betting['betting_data']
        
        print(f"\n💰 BETTING MARKET ANALYSIS")
        print("─" * 35)
        print(f"🎲 Vegas Favorite: {betting['vegas_favorite']}")
        print(f"📊 Vegas Confidence: {betting['vegas_confidence']:.1%}")
        print(f"💡 Market Analysis: {betting['market_analysis']}")
        
        if detailed:
            print(f"\n📊 Detailed Betting Data:")
            odds = betting_data['moneyline_odds']
            print(f"   • Moneyline Odds:")
            print(f"     - {info['team1']}: {odds[info['team1']]:+.0f}")
            print(f"     - {info['team2']}: {odds[info['team2']]:+.0f}")
            
            expert_picks = betting_data['expert_consensus']
            print(f"   • Expert Picks:")
            print(f"     - {info['team1']}: {expert_picks[info['team1']]} experts")
            print(f"     - {info['team2']}: {expert_picks[info['team2']]} experts")
            
            public_bet = betting_data['public_betting_percentage']
            print(f"   • Public Betting:")
            print(f"     - {info['team1']}: {public_bet[info['team1']]:.1%}")
            print(f"     - {info['team2']}: {public_bet[info['team2']]:.1%}")
            
            run_line = betting_data['run_line']
            print(f"   • Run Line: {run_line['favorite']} -{run_line['spread']:.1f} ({run_line['odds']:+.0f})")
            
            over_under = betting_data['over_under']
            print(f"   • Over/Under: {over_under['total']:.1f} (O: {over_under['over_odds']:+.0f}, U: {over_under['under_odds']:+.0f})")
    
    # Prediction Factors Breakdown
    print(f"\n🔬 PREDICTION FACTORS BREAKDOWN")
    print("─" * 40)
    factors = enhanced_pred['prediction_factors']
    print(f"🏈 Team Performance Model: {factors['team_performance']:.1%}")
    
    if 'weather_adjustment' in factors and factors['weather_adjustment'] != 0:
        print(f"🌤️  Weather Adjustment: {factors['weather_adjustment']:+.2f}")
    
    if 'betting_market_input' in factors and factors['betting_market_input'] != 0:
        print(f"💰 Betting Market Input: {factors['betting_market_input']:.1%}")
    
    # Basic vs Enhanced Comparison
    basic_winner = basic_pred['predicted_winner']
    enhanced_winner = enhanced_pred['final_winner']
    basic_prob = basic_pred['win_probability']
    enhanced_prob = enhanced_pred['final_win_probability']
    
    print(f"\n📊 MODEL COMPARISON")
    print("─" * 25)
    print(f"🔍 Basic Model:")
    print(f"   • Winner: {basic_winner}")
    print(f"   • Probability: {basic_prob:.1%}")
    print(f"✨ Enhanced Model:")
    print(f"   • Winner: {enhanced_winner}")
    print(f"   • Probability: {enhanced_prob:.1%}")
    
    if basic_winner != enhanced_winner:
        print(f"⚠️  PREDICTION CHANGE: Enhanced model flipped the prediction!")
    else:
        prob_change = enhanced_prob - basic_prob
        print(f"📈 Probability Adjustment: {prob_change:+.1%}")
    
    # Key Insights and Recommendations
    print(f"\n💡 KEY INSIGHTS & RECOMMENDATIONS")
    print("─" * 45)
    
    insights = []
    
    # Team strength insights
    score_diff = abs(team1_stats['overall_score'] - team2_stats['overall_score'])
    if score_diff < 3:
        insights.append("🔥 Very close matchup - could go either way")
    elif score_diff > 10:
        insights.append("🎯 Clear favorite based on team strength")
    
    # Weather insights
    if 'weather_analysis' in analysis:
        weather_adv = weather['net_advantage']['advantage']
        if weather_adv > 0.3:
            insights.append(f"🌤️  Weather significantly favors {weather['net_advantage']['team']}")
        elif weather_data.get('conditions') in ['rain', 'thunderstorm']:
            insights.append("⛈️  Poor weather may lead to unpredictable game")
    
    # Betting insights
    if 'betting_analysis' in analysis:
        if enhanced_winner != betting['vegas_favorite']:
            insights.append(f"💎 VALUE PLAY: Model disagrees with Vegas - consider {enhanced_winner}")
        
        expert_picks = betting_data['expert_consensus']
        public_bet = betting_data['public_betting_percentage']
        expert_fav = max(expert_picks, key=expert_picks.get)
        public_fav = max(public_bet, key=public_bet.get)
        
        if expert_fav != public_fav:
            insights.append(f"🧠 Sharp vs Public split: Experts like {expert_fav}, public backs {public_fav}")
    
    # Confidence insights
    if enhanced_pred['confidence_level'] == 'Low':
        insights.append("⚠️  Low confidence prediction - proceed with caution")
    elif enhanced_pred['confidence_level'] == 'High':
        insights.append("✅ High confidence prediction - strong betting opportunity")
    
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")
    
    if not insights:
        print("📊 Standard matchup with no major edge factors identified")
    
    print(f"\n{'='*80}")


def list_available_teams_enhanced(data_dir: str = "data/processed", season: int = 2024):
    """List all available teams with enhanced information"""
    
    teams_file = f"{data_dir}/team_scores_{season}.csv"
    if not os.path.exists(teams_file):
        print(f"❌ Team scores file not found: {teams_file}")
        print("   Run the comprehensive team fix first:")
        print(f"   python scripts/enhanced_comprehensive_team_fix.py --season {season} --force-all")
        return
    
    teams_df = pd.read_csv(teams_file)
    teams_df = teams_df.sort_values('overall_score', ascending=False)
    
    print(f"\n🏆 AVAILABLE TEAMS FOR ENHANCED ANALYSIS ({season} season)")
    print("=" * 70)
    print(f"{'Rank':<4} {'Team Name':<25} {'Overall':<8} {'Batting':<8} {'Pitching':<9} {'Fielding':<8}")
    print("-" * 70)
    
    for rank, (_, team) in enumerate(teams_df.iterrows(), 1):
        print(f"{rank:<4} {team['team_name']:<25} {team['overall_score']:<8.1f} "
              f"{team['batting_score']:<8.1f} {team['pitching_score']:<9.1f} {team['fielding_score']:<8.1f}")
    
    print(f"\n💡 Usage Examples:")
    print(f"   python scripts/enhanced_analyze_matchup.py \"Dodgers\" \"Yankees\" --detailed")
    print(f"   python scripts/enhanced_analyze_matchup.py \"Red Sox\" \"Astros\" --weather --betting")


def main():
    parser = argparse.ArgumentParser(description='Enhanced MLB matchup analysis with weather and betting data')
    parser.add_argument('team1', nargs='?', help='First team name')
    parser.add_argument('team2', nargs='?', help='Second team name')
    parser.add_argument('--season', type=int, default=2024, help='Season year')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis including all factors')
    parser.add_argument('--weather', action='store_true', help='Include weather analysis (default: enabled)')
    parser.add_argument('--betting', action='store_true', help='Include betting market analysis (default: enabled)')
    parser.add_argument('--no-weather', action='store_true', help='Disable weather analysis')
    parser.add_argument('--no-betting', action='store_true', help='Disable betting analysis')
    parser.add_argument('--list-teams', action='store_true', help='List all available teams')
    parser.add_argument('--data-dir', default='data/processed', help='Data directory')
    parser.add_argument('--weather-api-key', help='OpenWeatherMap API key for real weather data')
    parser.add_argument('--betting-api-key', help='Betting API key for real odds data')
    parser.add_argument('--save', help='Save analysis to JSON file')
    
    args = parser.parse_args()
    
    if args.list_teams:
        list_available_teams_enhanced(args.data_dir, args.season)
        return
    
    if not args.team1 or not args.team2:
        print("❌ Please provide two team names")
        print("Usage: python scripts/enhanced_analyze_matchup.py \"Team A\" \"Team B\"")
        print("\nUse --list-teams to see available teams")
        print("\nEnhanced Features:")
        print("  --detailed     : Show comprehensive analysis with all details")
        print("  --weather      : Include weather impact analysis (uses mock data by default)")
        print("  --betting      : Include betting market analysis (uses mock data by default)")
        print("  --weather-api-key YOUR_KEY : Use real weather data from OpenWeatherMap")
        print("  --betting-api-key YOUR_KEY : Use real betting data")
        return
    
    # Determine which features to include
    include_weather = True
    include_betting = True
    
    if args.no_weather:
        include_weather = False
    if args.no_betting:
        include_betting = False
    
    # Override if specifically requested
    if args.weather:
        include_weather = True
    if args.betting:
        include_betting = True
    
    try:
        analyzer = EnhancedMatchupAnalyzer(
            args.data_dir, 
            args.weather_api_key,
            args.betting_api_key
        )
        
        print(f"🔄 Analyzing enhanced matchup: {args.team1} vs {args.team2}")
        if include_weather and not args.weather_api_key:
            print("   ℹ️  Using mock weather data (provide --weather-api-key for real data)")
        if include_betting and not args.betting_api_key:
            print("   ℹ️  Using mock betting data (provide --betting-api-key for real data)")
        
        analysis = analyzer.analyze_enhanced_matchup(
            args.team1, 
            args.team2, 
            args.season,
            include_weather,
            include_betting
        )
        
        # Print comprehensive analysis
        print_enhanced_analysis(analysis, args.detailed)
        
        # Save if requested
        if args.save:
            with open(args.save, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"\n💾 Enhanced analysis saved to {args.save}")
        
        print(f"\n🎉 Enhanced matchup analysis complete!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure to run the scoring pipeline first:")
        print(f"   python scripts/enhanced_comprehensive_team_fix.py --season {args.season} --force-all")
        print(f"   python scripts/score_players.py --season {args.season}")
        print(f"   python scripts/score_teams.py --season {args.season}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
