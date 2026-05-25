# Orbit Wars - Kaggle Competition Overview

## Competition Name
**Orbit Wars** - A featured simulation competition

## Goal
Create and/or train AI bots to play a novel multi-agent 1v1 or 4-player FFA game against other submitted agents.

## Timeline
- **Start Date**: April 16, 2026
- **Entry Deadline**: June 16, 2026 (must accept rules)
- **Team Merger Deadline**: June 16, 2026
- **Final Submission Deadline**: June 23, 2026
- **Final Evaluation Period**: June 24, 2026 - ~July 8, 2026

All deadlines are at 11:59 PM UTC unless otherwise noted.

## Prizes
Total Prize Pool: $50,000

- 1st Place: $5,000
- 2nd Place: $5,000
- 3rd Place: $5,000
- 4th Place: $5,000
- 5th Place: $5,000
- 6th Place: $5,000
- 7th Place: $5,000
- 8th Place: $5,000
- 9th Place: $5,000
- 10th Place: $5,000

## Participation Stats
- 7,932 Entrants
- 3,467 Participants
- 3,245 Teams
- 6,152 Submissions

## Game Type
Real-time strategy game for 2 or 4 players.

## Submission Rules
- **Max submissions per day**: 5 agents per team
- **Tracked submissions**: Only latest 2 submissions are tracked
- **Best shown**: Only your best scoring bot appears on leaderboard
- **Initial rating**: New submissions start with μ₀ = 600

## Evaluation System
Each submission plays Episodes (games) against other bots with similar skill ratings:
- Skill ratings go up with wins
- Skill ratings go down with losses
- Tied games level out ratings
- Skill is modeled as Gaussian: N(μ, σ²)
- Newer bots play more frequently to get faster feedback
- All bots continue playing until competition ends

## Ranking System
Rating updates after each episode:
- Winning submissions: μ increases, opponent's μ decreases
- Tied games: μ values move toward their mean
- Update magnitude depends on rating deviation from expected result
- Uncertainty σ decreases with more information
- **Note**: Win/loss score does NOT affect skill rating, only the outcome

## Validation
- First game for each submission is a validation episode (plays against itself)
- If validation fails: marked as "Error", download logs to debug
- If validation passes: joins evaluation pool
