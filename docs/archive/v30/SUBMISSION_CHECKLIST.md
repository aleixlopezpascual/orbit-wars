# Orbit Wars Submission Checklist

## Week 1: Baseline Submission (v1)

### ✓ Completed
- [x] Dependencies installed (kaggle-environments 1.18.0+)
- [x] Baseline agent tested locally (5/5 tests passed)
  - Test 1: Basic observation ✓
  - Test 2: With enemy fleets ✓
  - Test 3: With comets ✓
  - Test 4: Low ship count ✓
  - Test 5: Empty actions ✓
- [x] Agent code copied to root (`agent.py`)
- [x] Agent returns valid action format
- [x] Sun collision detection verified (working)

### Next: Submit to Kaggle

The baseline agent is ready for submission. The agent implements:

**Core Features:**
1. **Sun collision detection** - Verifies fleet paths don't cross sun at (50, 50) with radius 10
2. **Target scoring** - Prioritizes planets by: `production * 12 + owner_bonus - ships*1.6 - distance*0.8`
3. **Fleet sizing** - Calculates required ships: `ceil(target_ships * 1.2 + 3.0)`
4. **Garrison preservation** - Keeps minimum 8 ships on each planet
5. **Safe launching** - Orders planets by strength, launches safer targets first

**Expected Performance:**
- ELO: ~600-650 (baseline)
- Win Rate: ~40-50% vs random agents
- Stability: No crashes, no invalid actions

### Submission Steps

1. **Go to Kaggle competition:**
   - https://www.kaggle.com/competitions/orbit-wars

2. **Create submission:**
   - Upload `agent.py` as the submission file
   - OR copy the agent code into Kaggle's code environment

3. **Configure submission:**
   - Set main agent function to `agent(observation)` from `agent.py`
   - Verify action format in game rules

4. **Monitor initial ELO:**
   - Record starting ELO after first submission
   - Expected: 600-650 ELO
   - Will take ~30-60 minutes for initial rating

### After Submission

Once v1 is submitted and rated:

**Week 2 Priorities (in order):**

1. **Implement forward simulator** (50-100 turns)
   - Predict planet positions after rotation
   - Predict comet locations
   - Estimate opponent expansion
   - → Target ELO: 750 (+100-150 ELO)

2. **Add multi-mission dispatch**
   - Priority queue: RESCUE → REINFORCE → CAPTURE → SNIPE
   - Coordinate launches from multiple planets
   - → Target ELO: 800-850 (+50-100 ELO)

3. **Implement comet evacuation**
   - Track comet spawn/expiry times
   - Evacuate 2 turns before expiry
   - Reclaim evacuated ships
   - → Target ELO: 850-900 (+50 ELO)

4. **Opponent modeling**
   - Track enemy planet ownership changes
   - Estimate opponent strategy
   - Adjust targeting accordingly
   - → Target ELO: 900-950 (+50-100 ELO)

5. **Fine-tuning & edge cases**
   - Handle asymmetric maps
   - Optimize garrison sizes
   - Fleet timing precision
   - → Target ELO: 950-1000+ (+50-100 ELO)

### Key Metrics to Track

After each submission, record:
- Date/time of submission
- v1/v2/v3 version
- Starting ELO
- Peak ELO
- Win rate (if available)
- Notable victories/losses

### Files

- `agent.py` - Main submission (baseline)
- `test_agent.py` - Local test harness
- `/baseline/agent.py` - Reference implementation
- `/docs/02_GAME_RULES.md` - Game mechanics reference
- `/research/orbit-wars-research.md` - Deep strategy research

### References

- Game Rules: See `/docs/02_GAME_RULES.md`
- Agent Interface: See `/docs/03_AGENT_INTERFACE.md`
- Fleet Speed Formula: See `/docs/06_DATA_UTILITIES.md` section 2.1
- Best Strategies: See `/research/orbit-wars-research.md` section 2

Good luck! 🚀
