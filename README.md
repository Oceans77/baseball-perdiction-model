# ⚾ Enhanced Baseball Prediction Model

A comprehensive machine learning system that predicts MLB game outcomes using advanced player statistics, weather analysis, and betting market integration for superior prediction accuracy.

## 🌟 Key Features

- **📊 Advanced Data Collection**: Automated gathering of player and team statistics from MLB's official API
- **🎯 Intelligent Player Scoring**: Advanced algorithm converting baseball statistics into comparable 0-100 scores
- **🏟️ Team Strength Analysis**: Sophisticated team ranking considering position importance and roster depth
- **🌤️ Weather Impact Integration**: Real-time weather analysis affecting pitching and batting performance
- **💰 Betting Market Analysis**: Integration with sportsbook odds and expert predictions
- **⚔️ Enhanced Matchup Analyzer**: Comprehensive head-to-head comparison with all factors
- **🔮 Superior Predictions**: Win probability calculations enhanced by weather and market data
- **📈 Detailed Terminal Output**: Complete analysis displayed in formatted terminal interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Internet connection (for data collection)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/baseball-prediction-model.git
cd baseball-prediction-model
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Enhanced Data Collection & Setup
```bash
# Complete enhanced setup (30+ teams with weather & betting integration)
make enhanced-setup

# Or run manually:
python scripts/standalone_enhanced_comprehensive_team_fix.py --season 2024 --force-all --quick-setup
```

### 5. Run Enhanced Analysis
```bash
# List available teams
make list-teams

# Enhanced matchup analysis
make enhanced-matchup TEAM1="Los Angeles Dodgers" TEAM2="New York Yankees"

# Or run directly with full features:
python scripts/enhanced_analyze_matchup.py "Dodgers" "Yankees" --detailed
```

## 🎯 Enhanced Usage Guide

### Basic Enhanced Analysis
```bash
# Quick enhanced prediction
python scripts/enhanced_analyze_matchup.py "Red Sox" "Astros"

# Detailed analysis with all factors
python scripts/enhanced_analyze_matchup.py "Giants" "Padres" --detailed

# List all available teams
python scripts/enhanced_analyze_matchup.py --list-teams
```

### Advanced Features

#### Weather Analysis
```bash
# Enhanced analysis with weather focus
python scripts/enhanced_analyze_matchup.py "Cubs" "Cardinals" --weather --detailed

# With real weather data (requires API key)
python scripts/enhanced_analyze_matchup.py "Mariners" "Angels" --detailed --weather-api-key YOUR_KEY
```

#### Betting Market Integration
```bash
# Analysis with betting market data
python scripts/enhanced_analyze_matchup.py "Dodgers" "Padres" --betting --detailed

# With real betting odds (requires API key)
python scripts/enhanced_analyze_matchup.py "Yankees" "Red Sox" --detailed --betting-api-key YOUR_KEY
```

#### Complete Enhanced Analysis
```bash
# Full analysis with all features
python scripts/enhanced_analyze_matchup.py "Astros" "Rangers" \
  --detailed \
  --weather-api-key YOUR_WEATHER_KEY \
  --betting-api-key YOUR_BETTING_KEY \
  --save analysis.json
```

## 📊 Enhanced Output Features

### Comprehensive Terminal Display
- **🎯 Enhanced Prediction**: Final winner with confidence levels
- **⚔️ Team Performance Comparison**: Detailed statistical breakdowns
- **🌤️ Weather Analysis**: Temperature, wind, humidity impacts on gameplay
- **💰 Betting Market Analysis**: Vegas odds, expert picks, public money
- **🔬 Prediction Factors**: Breakdown of all contributing factors
- **📊 Model Comparison**: Basic vs enhanced prediction differences
- **💡 Key Insights**: Value plays and strategic recommendations

### Weather Impact Factors
- **Temperature Effects**: Hot weather favors hitters, cold favors pitchers
- **Wind Analysis**: Impact on home runs and ball travel distance
- **Humidity Impact**: Effects on breaking ball movement
- **Pressure Systems**: High/low pressure effects on ball flight
- **Weather Conditions**: Rain, clear skies, etc. impact on performance

### Betting Market Integration
- **Moneyline Odds**: Real-time sportsbook odds and implied probabilities
- **Expert Consensus**: Professional handicapper picks and analysis
- **Public Betting**: Sharp money vs public betting splits
- **Value Identification**: When your model disagrees with Vegas
- **Run Lines & Totals**: Spread betting and over/under analysis

## 🛠️ Makefile Commands

```bash
# Enhanced Setup Commands
make enhanced-setup          # Complete enhanced setup
make enhanced-data          # Enhanced data collection only
make enhanced-test          # Test enhanced features

# Analysis Commands  
make list-teams             # List all available teams
make enhanced-matchup       # Interactive enhanced matchup analyzer
make enhanced-demo          # Run demonstration analysis

# Data Management
make clean-enhanced         # Clean enhanced data files
make update-data           # Update team data and scores
make validate-enhanced     # Validate enhanced system

# Development
make format                # Format code
make lint                  # Run code linting

# Help
make help-enhanced         # Show enhanced features help
```

## 🔑 API Integration

### Weather API (OpenWeatherMap)
1. Sign up at: https://openweathermap.org/api
2. Get your free API key (1,000 calls/day)
3. Use with: `--weather-api-key YOUR_KEY`

### Betting API (The Odds API)
1. Sign up at: https://the-odds-api.com/
2. Get your free API key (500 calls/month)
3. Use with: `--betting-api-key YOUR_KEY`

### Environment Variables (Recommended)
```bash
# Create .env file
echo "OPENWEATHER_API_KEY=your_weather_key" >> .env
echo "ODDS_API_KEY=your_betting_key" >> .env
```

## 📁 Project Structure

```
baseball-prediction-model/
├── 📄 README.md
├── 📋 requirements.txt
├── ⚙️ Makefile                                    # Enhanced automation
├── 📊 data/
│   ├── raw/                                      # Original collected data
│   └── processed/                               # Scored and analyzed data
├── 🧠 src/
│   ├── data_collection/                         # Data gathering modules
│   └── features/                               # Scoring algorithms
├── 🚀 scripts/
│   ├── enhanced_analyze_matchup.py             # 🌟 Enhanced matchup analyzer
│   └── standalone_enhanced_comprehensive_team_fix.py  # 🌟 Enhanced data collection
└── 📓 notebooks/                               # Analysis notebooks (optional)
```

## 📈 Sample Enhanced Analysis Output

```
🏟️  ENHANCED MLB MATCHUP ANALYSIS
================================================================================
📅 Analysis Date: 2024-07-01 15:30:45
🆚 Matchup: Los Angeles Dodgers vs New York Yankees
📊 Season: 2024

🎯 ENHANCED PREDICTION
──────────────────────────────
🏆 Predicted Winner: Los Angeles Dodgers
📈 Win Probability: 67.3%
🎚️  Confidence Level: High
📋 Breakdown:
   • Los Angeles Dodgers: 67.3%
   • New York Yankees: 32.7%

⚔️  TEAM PERFORMANCE COMPARISON
────────────────────────────────────────
Component       Team1           Team2           Advantage           
─────────────────────────────────────────────────────────────────
Overall Score   78.5            72.1            Los Angeles Dodgers (+6.4)
Batting Score   82.3            79.8            Los Angeles Dodgers (+2.5)
Pitching Score  81.7            74.2            Los Angeles Dodgers (+7.5)
Fielding Score  72.1            68.9            Los Angeles Dodgers (+3.2)

🌤️  WEATHER ANALYSIS
─────────────────────────
🏟️  Location: Los Angeles Dodgers (Home)
🌡️  Temperature: 78°F
💨 Wind: 6 mph
💧 Humidity: 65%
☁️  Conditions: Clear
📊 Impact Summary: Moderate temperature (78°F); Clear weather helps hitters

💰 BETTING MARKET ANALYSIS
───────────────────────────────────
🎲 Vegas Favorite: Los Angeles Dodgers
📊 Vegas Confidence: 61.2%
💡 Market Analysis: Strong consensus backing Los Angeles Dodgers

💡 KEY INSIGHTS & RECOMMENDATIONS
─────────────────────────────────────────────
1. 🎯 Clear favorite based on team strength
2. 🌤️  Weather significantly favors Los Angeles Dodgers
3. ✅ High confidence prediction - strong betting opportunity
```

## 🎮 Quick Examples

### Basic Enhanced Matchup
```bash
make enhanced-matchup TEAM1="Dodgers" TEAM2="Giants"
```

### Weather-Focused Analysis
```bash
python scripts/enhanced_analyze_matchup.py "Cubs" "Brewers" --weather --detailed
```

### Value Play Identification
```bash
python scripts/enhanced_analyze_matchup.py "Rays" "Orioles" --betting --detailed
```

### Complete Analysis with APIs
```bash
python scripts/enhanced_analyze_matchup.py "Astros" "Rangers" \
  --detailed \
  --weather-api-key $OPENWEATHER_API_KEY \
  --betting-api-key $ODDS_API_KEY
```

## 🔧 Troubleshooting

### Common Issues

**No Teams Available**
```bash
# Run enhanced data collection
make enhanced-setup
```

**API Connection Failed**
```bash
# Test with mock data first
python scripts/enhanced_analyze_matchup.py "Team A" "Team B" --detailed
```

**Missing Enhanced Features**
```bash
# Ensure enhanced scripts are in place
ls scripts/enhanced_*
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-enhancement`)
3. Commit your changes (`git commit -m 'Add amazing enhancement'`)
4. Push to the branch (`git push origin feature/amazing-enhancement`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MLB Stats API for providing free access to baseball data
- OpenWeatherMap for weather data integration
- The Odds API for betting market data
- The open source community for excellent Python libraries

---

**🎉 Ready to predict baseball games with enhanced accuracy? Start with `make enhanced-setup` and you'll be analyzing matchups with weather and betting data in minutes!**
