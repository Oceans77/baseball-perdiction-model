# Baseball Prediction Model - Makefile
# Comprehensive automation for the entire pipeline

.PHONY: help install test clean data lint format setup test-data full-pipeline check-env

# Default target
help:
	@echo "🏈 Baseball Prediction Model - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  install     - Install dependencies and create directories"
	@echo "  setup       - Complete setup (install + test data)"
	@echo "  check-env   - Check if environment is properly configured"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test        - Test API connectivity"
	@echo "  test-data   - Collect small sample of data for testing"
	@echo ""
	@echo "📊 Data Commands:"
	@echo "  data        - Collect full dataset"
	@echo "  score       - Score players and teams"
	@echo "  pipeline    - Run complete analysis pipeline"
	@echo ""
	@echo "🛠️  Development Commands:"
	@echo "  format      - Format code with black"
	@echo "  lint        - Run code linting with flake8"
	@echo "  clean       - Clean generated files"
	@echo "  clean-all   - Clean everything including data"
	@echo ""
	@echo "📈 Analysis Commands:"
	@echo "  analyze     - Analyze data quality only"
	@echo "  predict     - Generate team predictions"
	@echo "  rankings    - Show current team rankings"
	@echo ""
	@echo "Example: make setup && make pipeline"

# Installation and Setup
install:
	@echo "📦 Installing dependencies and setting up project..."
	pip install -r requirements.txt
	@echo "📁 Creating directory structure..."
	mkdir -p data/raw/player_stats
	mkdir -p data/raw/team_stats
	mkdir -p data/raw/game_results
	mkdir -p data/processed
	mkdir -p data/external
	mkdir -p notebooks
	mkdir -p tests
	mkdir -p logs
	touch data/raw/.gitkeep
	touch data/processed/.gitkeep
	touch data/external/.gitkeep
	@echo "✅ Installation complete!"

check-env:
	@echo "🔍 Checking environment..."
	@python --version || (echo "❌ Python not found" && exit 1)
	@pip list | grep pandas > /dev/null || (echo "❌ pandas not installed" && exit 1)
	@pip list | grep requests > /dev/null || (echo "❌ requests not installed" && exit 1)
	@test -d data/raw || (echo "❌ data/raw directory missing" && exit 1)
	@test -d src/data_collection || (echo "❌ src/data_collection directory missing" && exit 1)
	@echo "✅ Environment looks good!"

# Testing
test: check-env
	@echo "🧪 Testing API connectivity..."
	python scripts/quick_test.py

test-data: check-env
	@echo "📊 Collecting test data (10 players)..."
	python scripts/collect_data.py --max-players 10
	@echo "✅ Test data collection complete!"

# Data Collection
data: check-env
	@echo "📊 Collecting full dataset..."
	python scripts/collect_data.py
	@echo "✅ Data collection complete!"

data-teams-only: check-env
	@echo "🏟️ Collecting team data only..."
	python scripts/collect_data.py --teams-only

data-rosters-only: check-env
	@echo "👥 Collecting roster data only..."
	python scripts/collect_data.py --rosters-only

data-stats-only: check-env
	@echo "📈 Collecting player stats only..."
	python scripts/collect_data.py --stats-only

# Analysis
analyze: check-env
	@echo "🔍 Analyzing data quality..."
	python scripts/score_players.py --analyze-only

score: check-env
	@echo "🎯 Scoring players..."
	python scripts/score_players.py
	@echo "🏟️ Scoring teams..."
	python scripts/score_teams.py
	@echo "✅ Scoring complete!"

predict: check-env
	@echo "🔮 Generating predictions..."
	python scripts/score_teams.py --predictions 10

rankings: check-env
	@echo "🏆 Displaying current rankings..."
	@if [ -f data/processed/team_scores_2024.csv ]; then \
		echo "Top 10 Teams:"; \
		head -11 data/processed/team_scores_2024.csv | column -t -s,; \
	else \
		echo "❌ No rankings found. Run 'make score' first."; \
	fi

# Pipeline Commands
pipeline: check-env
	@echo "🚀 Running complete analysis pipeline..."
	@echo "Step 1/3: Collecting data..."
	python scripts/collect_data.py --max-players 100
	@echo "Step 2/3: Scoring players..."
	python scripts/score_players.py
	@echo "Step 3/3: Scoring teams and generating predictions..."
	python scripts/score_teams.py --predictions 5
	@echo "🎉 Pipeline complete!"

full-pipeline: check-env
	@echo "🚀 Running FULL analysis pipeline (may take 30+ minutes)..."
	@echo "Step 1/3: Collecting ALL data..."
	python scripts/collect_data.py
	@echo "Step 2/3: Scoring players..."
	python scripts/score_players.py
	@echo "Step 3/3: Scoring teams and generating predictions..."
	python scripts/score_teams.py --predictions 10
	@echo "🎉 Full pipeline complete!"

# Development
format:
	@echo "🎨 Formatting code..."
	black src/ scripts/ --line-length 100
	@echo "✅ Code formatting complete!"

lint:
	@echo "🔍 Running code linting..."
	flake8 src/ scripts/ --max-line-length=100 --ignore=E203,W503
	@echo "✅ Linting complete!"

# Cleaning
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf build dist *.egg-info
	rm -rf logs/*.log
	@echo "✅ Cleanup complete!"

clean-data:
	@echo "🧹 Cleaning data files..."
	rm -f data/raw/*.csv
	rm -f data/raw/player_stats/*.csv
	rm -f data/raw/team_stats/*.csv
	rm -f data/processed/*.csv
	rm -f data/processed/*.json
	@echo "✅ Data cleanup complete!"

clean-all: clean clean-data
	@echo "🧹 Deep cleaning everything..."
	@echo "✅ Complete cleanup done!"

# Convenience targets
setup: install test-data
	@echo "🎉 Project setup complete! Ready to use."
	@echo ""
	@echo "Next steps:"
	@echo "  make pipeline    - Run complete analysis"
	@echo "  make score       - Score existing data"
	@echo "  make predict     - Generate predictions"

# Status and Information
status:
	@echo "📊 Project Status"
	@echo "=================="
	@echo ""
	@echo "📁 Data Files:"
	@if [ -f data/raw/teams_2024.csv ]; then \
		echo "  ✅ Teams data: $(shell wc -l < data/raw/teams_2024.csv) lines"; \
	else \
		echo "  ❌ Teams data: Not found"; \
	fi
	@if [ -f data/raw/player_stats/player_stats_2024.csv ]; then \
		echo "  ✅ Player stats: $(shell wc -l < data/raw/player_stats/player_stats_2024.csv) lines"; \
	else \
		echo "  ❌ Player stats: Not found"; \
	fi
	@if [ -f data/processed/scored_players_2024.csv ]; then \
		echo "  ✅ Scored players: $(shell wc -l < data/processed/scored_players_2024.csv) lines"; \
	else \
		echo "  ❌ Scored players: Not found"; \
	fi
	@if [ -f data/processed/team_scores_2024.csv ]; then \
		echo "  ✅ Team scores: $(shell wc -l < data/processed/team_scores_2024.csv) lines"; \
	else \
		echo "  ❌ Team scores: Not found"; \
	fi
	@echo ""
	@echo "📋 Suggested next steps:"
	@if [ ! -f data/raw/teams_2024.csv ]; then \
		echo "  1. make test-data   # Start with sample data"; \
	elif [ ! -f data/processed/scored_players_2024.csv ]; then \
		echo "  1. make score       # Score the collected data"; \
	else \
		echo "  1. make predict     # Generate new predictions"; \
	fi

# Quick data collection for different seasons
data-2024:
	python scripts/collect_data.py --season 2024

data-2023:
	python scripts/collect_data.py --season 2023

# Help for specific commands
help-data:
	@echo "📊 Data Collection Commands:"
	@echo "  make data            - Collect full current season data"
	@echo "  make test-data       - Collect sample data (10 players)"
	@echo "  make data-teams-only - Only collect team information"
	@echo "  make data-2023       - Collect data for 2023 season"

help-analysis:
	@echo "📈 Analysis Commands:"
	@echo "  make analyze    - Check data quality without scoring"
	@echo "  make score      - Score players and teams"
	@echo "  make predict    - Generate matchup predictions"
	@echo "  make rankings   - Show current team rankings"
	@echo "  make pipeline   - Run complete analysis (recommended)"

# Validation
validate:
	@echo "✅ Validating project structure..."
	@test -f requirements.txt || (echo "❌ requirements.txt missing" && exit 1)
	@test -f src/data_collection/api_client.py || (echo "❌ API client missing" && exit 1)
	@test -f src/features/player_scoring.py || (echo "❌ Player scoring missing" && exit 1)
	@test -f src/features/team_scoring.py || (echo "❌ Team scoring missing" && exit 1)
	@test -f scripts/collect_data.py || (echo "❌ Data collection script missing" && exit 1)
	@test -f scripts/score_players.py || (echo "❌ Player scoring script missing" && exit 1)
	@test -f scripts/score_teams.py || (echo "❌ Team scoring script missing" && exit 1)
	@echo "✅ All essential files present!"

# Show project tree
tree:
	@echo "📁 Project Structure:"
	@if command -v tree >/dev/null 2>&1; then \
		tree -I '__pycache__|*.pyc|.git|venv|*.egg-info' -a; \
	else \
		find . -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' | head -30; \
	fi
