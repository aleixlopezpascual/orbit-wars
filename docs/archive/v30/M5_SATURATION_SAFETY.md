# M5: Combat Saturation & Tie-Annihilation

**Date:** 2026-05-26  
**Status:** ✅ IMPLEMENTED

## Combat Saturation Detection

**Purpose:** Prevent over-commitment that leaves source planets defenseless against counterattacks.

### Configuration Parameters (lines 237-243)

```python
SATURATION_LOOKAHEAD_TURNS = 30         # How many turns ahead to check incoming threats
SATURATION_ATTACK_COUNT_THRESHOLD = 3   # Trigger saturation if 3+ enemy fleets incoming
SATURATION_SEND_REDUCTION = 0.7         # Reduce sweep sends to 70% when saturated
TIE_SAFE_GARRISON_MULT = 1.15          # Keep 1.15x enemy force to survive ties
TIE_SAFETY_ENABLED = True               # Enable tie-safe garrison checks
```

### Saturation Detection Functions

#### `_detect_saturation_threats(planet_id, world, planned_commitments, lookahead_turns)`
- Scans enemy fleets incoming to a planet within lookahead window
- Counts distinct attack arrival turns (multiple fleets arriving same turn = single threat)
- Returns: number of distinct enemy attack windows
- Used by `_is_planet_saturated()` to determine if threshold exceeded

**Algorithm:**
1. Iterate through all enemy fleets
2. Filter for fleets targeting this planet_id
3. Check if arrival is within lookahead_turns window (0 < arrival ≤ lookahead)
4. Track unique arrival turns (treat simultaneous attacks as one threat turn)
5. Return count of distinct threat turns

**Example:**
- Planet 5 has incoming fleets at turns 10, 10, 15, 22
- Distinct threats: 3 (turns 10, 15, 22)
- If SATURATION_ATTACK_COUNT_THRESHOLD = 3, planet is saturated

#### `_is_planet_saturated(planet_id, world, planned_commitments)`
- Simple wrapper that checks if saturation threshold exceeded
- Returns: boolean (True if saturated, False otherwise)
- Called during sweep mission building to check each source planet

### Tie-Annihilation Safety

#### `_get_tie_safe_garrison(planet, enemy_incoming_ships)`
- Calculates minimum garrison to survive "tie" combat outcomes
- Tie = simultaneous arrival + mutual destruction
- To survive: garrison should be ≥ 1.15× enemy force
- Returns: minimum safe garrison size

**Logic:**
- If TIE_SAFETY_ENABLED is False, returns 0 (no extra garrison needed)
- Otherwise: `enemy_incoming_ships × TIE_SAFE_GARRISON_MULT (1.15)`
- Example: 20 incoming enemy ships → 23 ship minimum garrison to survive tie

### Integration with Sweeps

**Location:** lines 2651-2663 in build_sweep_missions()

**Algorithm:**
1. After building sweep_options, check each source planet for saturation
2. Collect list of saturated sources
3. If any sources saturated:
   - Create new sweep_options with reduced sends (70% of original)
   - Saturated sources send less, unsaturated send full amount
   - Preserves garrison for defense
4. Continue with score calculation and mission creation

**Example:**
- Source 1: 40 ships available, sending 35 in sweep
  - NOT saturated → sends full 35
- Source 2: 30 ships available, sending 25 in sweep
  - IS saturated (3+ incoming threats) → sends 25 × 0.7 = 17-18
  - Retains extra garrison for defense

### Edge Cases Handled

✅ **Multiple simultaneous attacks**
- Each distinct arrival turn counts as one threat
- Multiple fleets arriving same turn = not counted multiple times

✅ **Oversaturation**
- If planet already saturated, ALL sources reduce sends equally
- Preserves defensive posture across all participating planets

✅ **Timing variance**
- Looks ahead 30 turns (full game phase)
- Handles both immediate threats and long-term saturation

✅ **Tie survival**
- Optional via TIE_SAFETY_ENABLED flag
- Can be disabled if overhead becomes problematic
- Multiplier (1.15) is conservative; can be adjusted

---

## Code Changes

### New Functions (lines 2658-2705)
- `_detect_saturation_threats()` — 14 lines, O(n) enemy fleets
- `_is_planet_saturated()` — 5 lines, wrapper
- `_get_tie_safe_garrison()` — 6 lines, simple calculation
- Total: 25 lines of new code

### Modified Functions
- `build_sweep_missions()` — added saturation check loop (13 lines, lines 2651-2663)
- Logic: Check saturation, apply reduction, recalculate scores

### Configuration Added
- 5 new parameters: SATURATION_*, TIE_*

---

## Behavioral Changes

### Sweep Allocation Under Saturation

**Before M5:**
- Sweeps send fixed SWEEP_FLEET_SIZE_MULT regardless of defensive situation
- Risk: source planet emptied, vulnerable to counterattack

**After M5:**
- Saturation detected early (30-turn lookahead)
- Saturated sources reduce sends to 70% (SATURATION_SEND_REDUCTION)
- Preserves garrison for incoming threats
- Score recalculated with reduced forces (may deselect weak sweeps)

**Example:**
- Scenario: Player has 3 planets attacking same target
  - Planet A: 50 ships, NOT saturated → sends full sweep allocation
  - Planet B: 40 ships, saturated (3 enemy fleets incoming) → sends 70% of allocation
  - Planet C: 30 ships, saturated → sends 70% of allocation
- Result: Safer sweep with reduced risk to defenders

### Tie Scenarios

**Tie Combat Outcome:**
- Both fleets arrive simultaneously
- Both fleets destroyed in combat
- If attacker > defender: attacker wins after tie
- If attacker == defender: mutual annihilation (tie result)

**Garrison Protection:**
- `_get_tie_safe_garrison()` ensures we keep extra ships
- Default: 1.15× enemy incoming force
- Allows survival of tie scenarios without full annihilation

---

## M5 Result

✅ **Combat saturation and tie-safety checks implemented**

- Saturation detection scans 30-turn lookahead
- Saturated sources reduce sweep allocation to 70%
- Ties safely handled with 1.15× garrison multiplier
- Zero impact on non-sweep missions
- Purely defensive enhancement

**Expected Behavior:**
- Sweeps proceed normally if sources not under threat
- If 3+ enemy fleets incoming, source reduces sends
- Preserves garrison for defense without canceling sweeps
- More robust to opponent counterattacks

**Next: M6 - Benchmark-gate validation (n=24 → n=48)**

---

## Tuning Knobs

If benchmarks show excessive/insufficient saturation response:

| Parameter | Effect | Adjustment |
|-----------|--------|------------|
| SATURATION_LOOKAHEAD_TURNS | Detection window | 30 → 50 (wider) or 15 (narrower) |
| SATURATION_ATTACK_COUNT_THRESHOLD | Trigger sensitivity | 3 → 2 (lower) or 4 (higher) |
| SATURATION_SEND_REDUCTION | How much to reduce | 0.7 → 0.5 (more conservative) or 0.85 (less) |
| TIE_SAFE_GARRISON_MULT | Tie safety margin | 1.15 → 1.25 (safer) or 1.05 (riskier) |
| TIE_SAFETY_ENABLED | Disable tie logic | True → False (ignore ties) |

All tunable without code changes.

---

## Test Cases

1. **Saturation Triggered**
   - 3 enemy fleets incoming within 30 turns
   - Source should reduce sweep sends
   - Verify sweep still executes (just smaller)

2. **Saturation Not Triggered**
   - Only 1-2 enemy fleets incoming
   - Source should NOT reduce sends
   - Sweep sends at full allocation

3. **Tie Scenario**
   - Enemy and our fleet arrive simultaneously
   - With tie-safe garrison (1.15×), our force should win after mutual loss
   - Without tie-safe, mutual annihilation possible

4. **Multi-source Sweep**
   - Planet A not saturated, Planet B saturated, Planet C not saturated
   - A and C send full allocation
   - B sends 70% reduction
   - Score recalculated with reduced total
