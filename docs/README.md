# Orbit Wars - Kaggle Competition Documentation Index

Welcome! This directory contains all documentation for the Orbit Wars Kaggle competition. Use this as your reference guide throughout the competition.

## Quick Navigation

### 📋 Competition Details
**File**: `01_COMPETITION_OVERVIEW.md`
- Competition goals and prizes ($50,000 total)
- Timeline and deadlines (Final submission: June 23, 2026)
- Submission rules (5 per day, best 2 tracked)
- Evaluation and ranking system (Elo-like skill ratings)
- Participation stats (7,932 entrants, 3,467 participating)

### 🎮 Game Rules & Mechanics
**File**: `02_GAME_RULES.md`
- Complete board layout (100x100 space with sun at center)
- Planet mechanics (orbiting vs static, production, capture)
- Fleet mechanics (speed scaling, movement, collision detection)
- Comet rules (temporary planets on elliptical orbits)
- Turn order (7-step cycle from comet removal to combat)
- Combat resolution (multi-fleet engagements)
- Scoring and win conditions
- Configuration parameters

### 🤖 Agent Interface Specification
**File**: `03_AGENT_INTERFACE.md`
- Agent function signature and input/output format
- Complete observation schema (planets, fleets, player, etc.)
- Action format (moves: from_planet_id, angle, ships)
- Named tuples for convenience (Planet, Fleet, CENTER constants)
- Move constraints and validation rules
- Example implementations (nearest target, spreading strategies)
- Local testing methods

### 📤 Submission & Testing Guide
**File**: `04_SUBMISSION_GUIDE.md`
- Prerequisites (Kaggle CLI, API authentication)
- Joining the competition
- Local testing and validation
- Submission formats (single file, multi-file, notebook)
- Monitoring submissions and episodes
- Downloading replays and logs for analysis
- Typical development workflow
- Key constraints and deadlines

### 📊 Data Structures Reference
**File**: `05_DATA_STRUCTURES.md`
- Complete observation schema (planets, fleets, player info)
- Planet data format and properties
- Fleet data format and properties
- Initial planets for rotation prediction
- Comet data structures
- Action/move format and constraints
- Angle convention and calculations
- Data access patterns (arrays vs named tuples)

### 🛠️ Data Utilities & Analysis
**File**: `06_DATA_UTILITIES.md`
- Fleet speed calculation
- Planet rotation prediction
- Comet position prediction
- Distance and travel time calculations
- Collision detection (sun & planets)
- Decision-making patterns (target selection, force calculation)
- Game state analysis (ship counts, threat assessment)
- Logging and debugging helpers

### 🎓 Getting Started Tutorial
**File**: `07_GETTING_STARTED_TUTORIAL.md`
- Environment setup and installation
- Understanding observations and actions
- Building your first agent (Nearest Planet Sniper)
- Testing locally (1v1 and 4-player games)
- Agent limitations and improvements
- Creating submission files
- Submission methods (browser, CLI, notebook)
- Troubleshooting guide

## Key Dates to Remember

| Date | Event |
|------|-------|
| April 16, 2026 | Competition starts |
| June 16, 2026 | Entry & team merger deadline |
| June 23, 2026 | Final submission deadline |
| June 24 - July 8 | Final evaluation period |

## Competition Facts at a Glance

- **Type**: Real-time strategy simulation for 2 or 4 players
- **Board**: 100x100 continuous 2D space
- **Game length**: 500 turns per episode
- **Decision time**: 1 second per turn
- **Ranking system**: Elo-like skill ratings (μ, σ)
- **Rating update**: After each episode based on outcome
- **Submissions tracked**: Latest 2 per team
- **Leaderboard shows**: Your highest-rated submission only
- **Validation**: First game tests your agent against itself

## Core Game Concepts

### Winning Strategy
Final score = total ships on planets + total ships in fleets (highest wins)

### Key Resources
- **Planets**: Generate ships per turn (production 1-5)
- **Fleets**: Mobile units that capture planets through combat
- **Comets**: Temporary high-value planets spawning at game steps 50, 150, 250, 350, 450

### Map Features
- **Sun** (50, 50): Destroys fleets that cross it
- **Orbiting planets**: Rotate around sun (inner planets < orbital_radius + planet_radius ≤ 50)
- **Static planets**: Don't rotate (outer planets)
- **4-fold symmetry**: Ensures fairness across starting positions

## Getting Started Checklist

- [ ] Read `01_COMPETITION_OVERVIEW.md` for timeline and evaluation rules
- [ ] Study `02_GAME_RULES.md` to understand all mechanics
- [ ] Review `03_AGENT_INTERFACE.md` for agent implementation details
- [ ] Follow `04_SUBMISSION_GUIDE.md` to set up local testing
- [ ] Write and test a simple agent (nearest planet sniper is a good baseline)
- [ ] Submit first agent and monitor ratings
- [ ] Iterate and improve

## Resources

### External Links
- **Competition Page**: https://www.kaggle.com/competitions/orbit-wars
- **Kaggle CLI Docs**: https://github.com/Kaggle/kaggle-api
- **Starter Kits**: Available on competition page

### Required Installations
```bash
pip install kaggle kaggle-environments>=1.28.0
```

### API Setup
```bash
mkdir -p ~/.kaggle
# Download token from https://www.kaggle.com/settings/api
nano ~/.kaggle/access_token
chmod 600 ~/.kaggle/access_token
```

## Agent Development Tips

### Baseline Strategy
Start with the "nearest planet sniper" from the starter kit:
1. Find all planets you don't own
2. From each of your planets, attack the nearest enemy/neutral planet
3. Send enough ships to guarantee capture (target.ships + 1)

### Performance Optimization
- **Decision time**: 1 second per turn (use `remainingOverageTime` if needed)
- **Observation size**: Small observations (typically <50 planets, <100 fleets)
- **Computation**: Can do medium calculations within 1 second

### Strategy Considerations
- Early game: Capture nearby neutral planets for production
- Mid game: Defend against player threats while expanding
- Late game: Concentrate fleet power to overwhelm opponents
- Comet timing: Prepare to capture comets when they spawn (at steps 50, 150, 250, 350, 450)

## Notes

- All deadlines in UTC
- Elo ratings updated continuously (not batched)
- New submissions start at μ₀ = 600 with high uncertainty
- Your rating improves faster early, then stabilizes as σ decreases
- Only your best submission affects final ranking
- But all submissions can provide feedback on different strategies

---

**Last Updated**: Competition begins April 16, 2026
**Documentation Version**: 1.0
