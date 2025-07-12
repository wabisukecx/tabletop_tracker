# TabletopTracker - Comprehensive Tabletop Game Statistics Management

A powerful Streamlit application for tracking, analyzing, and managing tabletop game sessions with intelligent statistical insights. Features BoardGameGeek integration, custom score sheets, cooperative/competitive game support, and comprehensive multi-language interface.

## Key Features

### Smart Game Management

- **BGG Integration**: Direct search and import from BoardGameGeek with detailed game information
- **Multi-language Names**: Intelligent display of Japanese/English game names with automatic detection
- **Game Rankings**: Real-time BGG ranking data with category-specific rankings
- **Image Support**: Automatic box art display with fallback handling

### Advanced Play Recording

- **Custom Score Sheets**: Game-specific scoring systems for competitive and cooperative games
- **Cooperative Game Support**: Proper win/loss tracking for team-based games
- **Detailed Statistics**: Player performance tracking with accurate win rate calculations
- **Play History**: Comprehensive session logging with notes and locations

### Statistical Analysis

- **Player Analytics**: Individual win rates, play counts, and performance trends
- **Game Insights**: Play frequency, average duration, and popularity metrics
- **Visual Charts**: Interactive graphs using Plotly for data visualization
- **Monthly Trends**: Timeline analysis of gaming activity

### Data Management

- **YAML Storage**: Human-readable data files with independent backup capability
- **Multi-file Architecture**: Separated data types for optimal performance and reliability
- **Backup System**: One-click backup creation with timestamp organization
- **Data Integrity**: Robust error handling and validation

---

## Core Functions

| Function | Description | Key Benefits |
|----------|-------------|--------------|
| **Game Search & Import** | BGG database integration with pagination | Quick game registration with comprehensive metadata |
| **Custom Score Sheets** | Game-specific scoring templates | Accurate recording for complex games |
| **Play Session Recording** | Detailed game session logging | Complete play history with player statistics |
| **Statistical Dashboard** | Multi-dimensional analytics | Performance insights and trends visualization |
| **Data Export/Backup** | YAML-based data management | Portable, human-readable data storage |

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/TabletopTracker.git
cd TabletopTracker

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run main.py
```

### Basic Usage

1. **Add Players**: Register players who will participate in game sessions
2. **Import Games**: Search and add games from BoardGameGeek database
3. **Create Score Sheets**: Design custom scoring templates for specific games
4. **Record Sessions**: Log game plays with scores and session details
5. **View Statistics**: Analyze player performance and game popularity trends

---

## Application Structure

### Core Modules

| Module | Purpose | Features |
|--------|---------|----------|
| **`main.py`** | Application entry point | Page routing, session management |
| **`language_manager.py`** | Multi-language support | Dynamic language switching |
| **`data_manager.py`** | Data persistence layer | YAML file operations, backup |
| **`bgg_api.py`** | BoardGameGeek integration | Game search, metadata retrieval |
| **`score_sheet_manager.py`** | Custom scoring systems | Template creation and management |
| **`utils.py`** | Utility functions | Player statistics calculations |

### UI Components

```bash
ui_common.py              # Shared interface elements
ui_game_management.py     # Game search and registration
ui_player_management.py   # Player registration and stats
ui_play_recording.py      # Session logging interface
ui_score_sheet.py         # Score sheet designer
ui_statistics.py          # Analytics dashboard
ui_settings.py            # Configuration management
```

### Data Structure

```bash
data/
├── games.yaml          # Game metadata from BGG
├── players.yaml        # Player registration data
├── plays.yaml          # Game session records
└── score_sheets.yaml   # Custom scoring templates

language/
├── settings.yaml       # Language preferences
├── ja.yaml            # Japanese translations
└── en.yaml            # English translations
```

---

## Advanced Features

### Score Sheet System

#### Competitive Games

```yaml
fields:
  - name: "Resource Collection"
    type: "number"
    default: 0
  - name: "Bonus Objectives"
    type: "checkbox"
    points: 5
```

#### Cooperative Games

```yaml
fields:
  - name: "Game Result"
    type: "choice"
    options: ["Victory", "Defeat"]
    global: true
  - name: "Player Role"
    type: "choice"
    options: ["Role1", "Role2", "Role3"]
    global: false
```

### Statistical Calculations

#### Win Rate Algorithm

- **Competitive Games**: Winner = highest scorer
- **Cooperative Games**: All players share same result
- **Tie Handling**: Multiple winners for equal scores

#### Performance Metrics

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| **Play Count** | Total sessions participated | Activity level |
| **Win Count** | Victories across all games | Success rate |
| **Win Rate** | Wins / Total Plays × 100 | Performance percentage |
| **Average Duration** | Total time / Total plays | Session length trends |

---

## BGG Integration

### API Features

- **Search**: Fuzzy matching with result pagination
- **Game Details**: Comprehensive metadata retrieval
- **Multi-language Names**: Japanese/English name extraction
- **Rankings**: Real-time BGG ranking data
- **Images**: Automatic box art downloading

### Rate Limiting & Error Handling

```python
# Built-in retry logic with exponential backoff
max_retries = 3
timeout = 15 seconds
response_codes: 200 (success), 202 (processing), 4xx/5xx (error)
```

### Data Quality

- **Name Validation**: Ensures valid game names before storage
- **Duplicate Prevention**: Checks for existing games before addition
- **Image Fallback**: Graceful handling of missing artwork
- **Ranking Updates**: Manual refresh option for latest data

---

## Language Support

### Supported Languages

- **Japanese (ja)**: Full interface with native game name support
- **English (en)**: Complete translation with international game names

### Game Name Intelligence

| Scenario | Display Logic |
|----------|---------------|
| **Japanese Mode** | Japanese name → English fallback → Primary name |
| **English Mode** | English name → Japanese fallback → Primary name |
| **File Operations** | Always use BGG ID for consistency |
| **Search Results** | Show both names when available |

### Adding New Languages

1. Create `language/{code}.yaml` following existing structure
2. Add language detection in `language_manager.py`
3. Test interface completeness
4. Ensure proper UTF-8 encoding

---

## Data Management Architecture

### File Independence

Each data type operates independently for optimal reliability:

| File | Dependencies | Backup Priority |
|------|--------------|----------------|
| `games.yaml` | BGG API data | High |
| `players.yaml` | User input only | Medium |
| `plays.yaml` | Games + Players | Critical |
| `score_sheets.yaml` | Games reference | Medium |

### Backup Strategy

```bash
# Automatic backup creation
backup_YYYYMMDD_HHMMSS/
├── games.yaml
├── players.yaml
├── plays.yaml
└── score_sheets.yaml
```

### Data Validation

- **Referential Integrity**: Validates game/player references
- **Format Checking**: YAML syntax validation
- **Encoding Safety**: UTF-8 enforcement
- **Recovery Options**: Automatic backup restoration

---

## Performance Optimizations

### Caching Strategy

- **Session State**: UI component caching
- **BGG Responses**: 24-hour TTL for game data
- **Image Loading**: Lazy loading with error handling
- **Search Results**: Pagination for large result sets

### Memory Management

- **Selective Loading**: Only load required data sections
- **Garbage Collection**: Automatic cleanup of unused objects
- **File Streaming**: Efficient YAML processing
- **Image Optimization**: Thumbnail generation for box art

---

## Configuration Options

### BGG API Settings

```python
BASE_URL = "https://boardgamegeek.com/xmlapi2"
TIMEOUT = 15  # seconds
MAX_RETRIES = 3
RATE_LIMIT = 1  # request per second
```

### Score Sheet Templates

```yaml
# Competitive game template
competitive_template:
  game_type: "Competitive Game"
  fields: [{"name": "Score", "type": "number", "default": 0}]

# Cooperative game template  
cooperative_template:
  game_type: "Cooperative Game"
  fields: [{"name": "Result", "type": "choice", "global": true}]
```

---

## Deployment Options

### Local Development

```bash
# Standard installation
pip install streamlit pandas plotly PyYAML requests

# Development mode with auto-reload
streamlit run main.py --server.runOnSave=true
```

### Production Deployment

```bash
# Streamlit Community Cloud
# 1. Push to GitHub
# 2. Connect repository at share.streamlit.io
# 3. Configure environment variables

# Self-hosted
# 1. Install dependencies
# 2. Configure reverse proxy (nginx/apache)
# 3. Set up process manager (systemd/supervisor)
```

## API Usage & Costs

### BoardGameGeek API

- **Free Service**: No API key required
- **Rate Limiting**: ~1 request per second recommended
- **Data Access**: Full game database with search and details
- **Reliability**: Community-maintained, high uptime

### Resource Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 512MB | 1GB+ |
| **Storage** | 100MB | 500MB+ |
| **Network** | Basic internet | Stable broadband |
| **Python** | 3.8+ | 3.9+ |

---

## Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **BGG API Timeout** | Search fails, games won't load | Check internet connection, retry after delay |
| **YAML Encoding Error** | Data won't save, Unicode errors | Ensure UTF-8 encoding, avoid special characters |
| **Missing Images** | Box art not displaying | Normal behavior, BGG image server limitations |
| **Language Switching** | Interface doesn't change | Clear browser cache, restart application |
| **Score Sheet Errors** | Forms not submitting | Validate all required fields completed |

### Debug Mode

```bash
# Enable verbose logging
streamlit run main.py --logger.level=debug

# Check data integrity
python -c "from data_manager import DataManager; dm = DataManager(); print(dm.get_data_info())"

# Validate YAML files
python -c "import yaml; yaml.safe_load(open('data/games.yaml', 'r', encoding='utf-8'))"
```

### Data Recovery

```python
# Restore from backup
import shutil
shutil.copytree('backup_20241212_143022/', 'data/')

# Validate restored data
from data_manager import DataManager
dm = DataManager()
print(f"Games: {len(dm.data['games'])}")
print(f"Players: {len(dm.data['players'])}")
print(f"Plays: {len(dm.data['plays'])}")
```

---

## Contributing

### Development Setup

```bash
# Fork repository and clone
git clone https://github.com/your-username/TabletopTracker.git
cd TabletopTracker

# Create development branch
git checkout -b feature/new-feature

# Install development dependencies
pip install -r requirements.txt
```

### Code Standards

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Docstrings for all functions
- **Error Handling**: Comprehensive exception management
- **Testing**: Manual testing procedures documented

### Pull Request Process

1. Create feature branch from main
2. Implement changes with proper documentation
3. Test all functionality manually
4. Update relevant documentation
5. Submit pull request with detailed description

### Adding New Features

| Feature Type | Required Changes |
|--------------|------------------|
| **New Page** | Add UI module, update main.py routing, add translations |
| **New Data Type** | Extend data_manager.py, add YAML schema |
| **New Language** | Create language file, test interface completeness |
| **BGG Enhancement** | Update bgg_api.py, handle new data fields |

---

## Version 1.0 (Current)

- **Core Functionality**: Complete game tracking and statistics
- **BGG Integration**: Full search and import capabilities
- **Multi-language**: Japanese/English support
- **Score Sheets**: Custom competitive/cooperative templates
- **Data Management**: YAML-based storage with backup

---

## License & Acknowledgments

**License**: MIT License - Free for personal, educational, and commercial use

**Data Sources**:

- BoardGameGeek API for comprehensive game database
- Community translations and localization
- User-contributed score sheet templates

**Special Thanks**:

- BoardGameGeek community for maintaining the world's largest board game database
- Streamlit team for the excellent web application framework
- Contributors to Japanese localization and game name databases
- Beta testers and early adopters providing valuable feedback

**Dependencies**:

- Streamlit: Web application framework
- Plotly: Interactive data visualization
- PyYAML: Human-readable data serialization
- Requests: HTTP library for BGG API
- Pandas: Data analysis and manipulation
