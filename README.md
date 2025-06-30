# ⚾ Baseball Prediction Model

A comprehensive machine learning system that predicts MLB game outcomes based on advanced player statistics and team performance metrics.

## 🌟 Features

- **📊 Data Collection**: Automated gathering of player and team statistics from MLB's official API
- **🎯 Player Scoring**: Advanced algorithm that converts baseball statistics into comparable 0-100 scores
- **🏟️ Team Scoring**: Intelligent team strength calculation considering position importance and roster depth
- **🔮 Game Predictions**: Win probability calculations for any team matchup
- **📈 Rankings**: Complete team rankings with detailed performance breakdowns
- **⚡ Real-time Analysis**: Fresh data collection and scoring for current season

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

### 4. Create Directory Structure
```bash
# Using make (recommended)
make install

# Or manually:
mkdir -p data/{raw/{player_stats,team_stats,game_results},processed,external}
mkdir -p {notebooks,tests,docs}
```

### 5. Test the System
```bash
# Test API connectivity
python scripts/quick_test.py
```

### 6. Run Complete Analysis
```bash
# Option 1: Full automated pipeline
make setup

# Option 2: Step by step
python scripts/collect_data.py --max-players 50  # Start small
python scripts/score_players.py
python scripts/score_teams.py
```

## 📋 Usage Guide

### Data Collection

#### Basic Data Collection
```bash
# Collect all data for current season
python scripts/collect_data.py

# Collect specific amount of player data
python scripts/collect_data.py --max-players 100

# Collect for different season
python scripts/collect_data.py --season 2023
```

#### Data Collection Flags
| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--season` | Year to collect data for | 2024 | `--season 2023` |
| `--max-players` | Maximum players to collect stats for | 100 | `--max-players 200` |
| `--teams-only` | Only collect team information | False | `--teams-only` |
| `--rosters-only` | Only collect player rosters | False | `--rosters-only` |
| `--stats-only` | Only collect player statistics | False | `--stats-only` |

#### Examples
```bash
# Quick test with limited data
python scripts/collect_data.py --max-players 10

# Collect only team rosters
python scripts/collect_data.py --rosters-only

# Full collection for 2023 season
python scripts/collect_data.py --season 2023 --max-players 500
```

### Player Scoring

#### Basic Player Scoring
```bash
# Score all collected players
python scripts/score_players.py

# Score players from specific season
python scripts/score_players.py --season 2023
```

#### Player Scoring Flags
| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--season` | Season year to score | 2024 | `--season 2023` |
| `--data-dir` | Directory containing raw data | data | `--data-dir custom_data` |
| `--output-dir` | Directory to save scored data | data/processed | `--output-dir results` |
| `--analyze-only` | Only analyze data quality, don't score | False | `--analyze-only` |

#### Examples
```bash
# Analyze data quality before scoring
python scripts/score_players.py --analyze-only

# Score players and save to custom directory
python scripts/score_players.py --output-dir my_results

# Score players from 2023 season
python scripts/score_players.py --season 2023 --data-dir historical_data
```

### Team Scoring

#### Basic Team Scoring
```bash
# Calculate team scores and rankings
python scripts/score_teams.py

# Generate extra predictions
python scripts/score_teams.py --predictions 10
```

#### Team Scoring Flags
| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--season` | Season year to score | 2024 | `--season 2023` |
| `--input-dir` | Directory with scored players | data/processed | `--input-dir results` |
| `--output-dir` | Directory to save team scores | data/processed | `--output-dir final_results` |
| `--predictions` | Number of sample predictions | 5 | `--predictions 10` |

#### Examples
```bash
# Basic team scoring
python scripts/score_teams.py

# Generate many sample predictions
python scripts/score_teams.py --predictions 15

# Process data from custom directories
python scripts/score_teams.py --input-dir my_data --output-dir my_results
```

## 🛠️ Makefile Commands

For convenience, use these make commands:

```bash
# Install dependencies and create directories
make install

# Run API connectivity test
make test

# Collect sample data (10 players)
make test-data

# Collect full dataset
make data

# Format code
make format

# Run linting
make lint

# Clean generated files
make clean

# Complete setup (install + test data)
make setup
```

## 📁 Project Structure

```
baseball-prediction-model/
├── 📄 README.md
├── 📋 requirements.txt
├── ⚙️ config/
│   └── config.yaml
├── 📊 data/
│   ├── raw/                 # Original collected data
│   ├── processed/           # Scored and analyzed data
│   └── external/           # External data sources
├── 🧠 src/
│   ├── data_collection/    # Data gathering modules
│   └── features/           # Scoring algorithms
├── 🤖 scripts/
│   ├── collect_data.py     # Data collection automation
│   ├── score_players.py    # Player scoring automation
│   ├── score_teams.py      # Team scoring automation
│   └── quick_test.py       # System testing
└── 📓 notebooks/           # Analysis notebooks
```

## 📊 Output Files

After running the complete pipeline, you'll have:

### Data Files
- `data/raw/teams_2024.csv` - All MLB teams
- `data/raw/player_stats/rosters_2024.csv` - All player rosters
- `data/raw/player_stats/player_stats_2024.csv` - Individual player statistics
- `data/raw/team_stats/team_stats_2024.csv` - Team-level statistics

### Analysis Files
- `data/processed/scored_players_2024.csv` - Players with calculated scores
- `data/processed/team_scores_2024.csv` - Team rankings and scores
- `data/processed/team_scores_detailed_2024.json` - Detailed team analysis

## 🎯 Example Workflow

Here's a complete example workflow:

```bash
# 1. Set up environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
make install

# 2. Test connectivity
python scripts/quick_test.py

# 3. Collect data (start small)
python scripts/collect_data.py --max-players 50

# 4. Score players
python scripts/score_players.py

# 5. Score teams and get predictions
python scripts/score_teams.py --predictions 8

# 6. Check results
ls data/processed/
head data/processed/team_scores_2024.csv
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
data_collection:
  season: 2024
  max_players_per_run: 100
  delay_between_requests: 0.5
  data_directory: "data/raw"

api_settings:
  mlb_stats_api:
    base_url: "https://statsapi.mlb.com/api/v1"
    timeout: 30
    max_retries: 3
```

## 🚨 Troubleshooting

### Common Issues

**API Connection Failed**
```bash
# Test your internet connection and try again
python scripts/quick_test.py
```

**Missing Data Files**
```bash
# Make sure data collection completed successfully
python scripts/collect_data.py --teams-only
```

**Import Errors**
```bash
# Ensure you're in the project directory and virtual environment is activated
pwd
which python
pip list
```

**Permission Errors**
```bash
# Make sure directories exist and are writable
chmod 755 data/
mkdir -p data/{raw,processed}
```

### Getting Help

1. **Check logs** - Scripts provide detailed logging of what's happening
2. **Start small** - Use `--max-players 10` to test with limited data
3. **Test components** - Use `--analyze-only` or `--teams-only` flags
4. **Clean slate** - Use `make clean` to remove generated files and start over

## 📈 Understanding the Output

### Player Scores (0-100 scale)
- **Batting Score**: Hitting performance (avg, OBP, power)
- **Pitching Score**: Pitching effectiveness (ERA, WHIP, strikeouts)
- **Fielding Score**: Defensive ability (fielding %, errors)
- **Overall Score**: Position-weighted combination of all skills

### Team Scores
- **Overall Score**: Weighted team strength considering all positions
- **Component Scores**: Team averages for batting, pitching, fielding
- **Depth Score**: Quality of bench players and roster completeness

### Predictions
- **Win Probability**: Chance of team winning (0-100%)
- **Score Difference**: Gap between team strengths
- **Component Advantages**: Which team is stronger in each area

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MLB Stats API for providing free access to baseball data
- The open source community for excellent Python libraries

---

**🎉 Ready to predict some baseball games? Start with `make setup` and you'll be ranking teams in minutes!**
