# Orbit Wars - Data Structures Reference

This document describes all data structures used in the game, including observation data, action data, and internal representations.

## Observation Data

The `obs` dictionary received by your agent contains the following fields:

### Planets

**Field**: `planets`
**Type**: `List[List]` or `List[Planet]` (when using named tuple)
**Format**: `[[id, owner, x, y, radius, ships, production], ...]`

Each planet is represented as an array with 7 elements:

| Index | Name | Type | Range | Description |
|-------|------|------|-------|-------------|
| 0 | id | int | ≥ 0 | Unique planet identifier |
| 1 | owner | int | -1 to 3 | -1=neutral, 0-3=player ID |
| 2 | x | float | 0-100 | X coordinate on board |
| 3 | y | float | 0-100 | Y coordinate on board |
| 4 | radius | float | >0 | Physical radius (1 + ln(production)) |
| 5 | ships | int | ≥ 0 | Current garrison |
| 6 | production | int | 1-5 | Ships generated per turn |

**Example**:
```python
planets = obs["planets"]
# [0, -1, 50.0, 30.5, 2.1, 25, 3]
# Planet 0, neutral, at (50, 30.5), radius 2.1, 25 ships, production 3

# Using named tuple
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
planet = Planet(*planets[0])
print(f"Planet {planet.id}: owner={planet.owner}, ships={planet.ships}")
```

### Fleets

**Field**: `fleets`
**Type**: `List[List]` or `List[Fleet]` (when using named tuple)
**Format**: `[[id, owner, x, y, angle, from_planet_id, ships], ...]`

Each fleet is represented as an array with 7 elements:

| Index | Name | Type | Range | Description |
|-------|------|------|-------|-------------|
| 0 | id | int | ≥ 0 | Unique fleet identifier |
| 1 | owner | int | 0-3 | Player ID who owns the fleet |
| 2 | x | float | 0-100 | Current X coordinate |
| 3 | y | float | 0-100 | Current Y coordinate |
| 4 | angle | float | 0-2π | Direction in radians |
| 5 | from_planet_id | int | ≥ 0 | Source planet ID |
| 6 | ships | int | ≥ 1 | Number of ships (fixed) |

**Example**:
```python
fleets = obs["fleets"]
# [5, 0, 45.2, 50.0, 0.785, 2, 100]
# Fleet 5, owned by player 0, at (45.2, 50), heading π/4 radians,
# launched from planet 2, contains 100 ships

# Using named tuple
from kaggle_environments.envs.orbit_wars.orbit_wars import Fleet
fleet = Fleet(*fleets[0])
print(f"Fleet {fleet.id}: {fleet.ships} ships heading {fleet.angle} rad")
```

### Player & Game State

**Field**: `player`
**Type**: `int`
**Range**: 0-3
**Description**: Your player ID in this game

**Field**: `angular_velocity`
**Type**: `float`
**Range**: 0.025-0.05
**Description**: Rotation speed of inner planets (radians/turn)

**Field**: `remainingOverageTime`
**Type**: `float`
**Range**: ≥ 0
**Description**: Remaining time budget for complex computations (seconds)

**Example**:
```python
player_id = obs["player"]  # 0, 1, 2, or 3
angular_vel = obs["angular_velocity"]  # ~0.04 radians/turn
time_budget = obs["remainingOverageTime"]  # e.g., 30.5 seconds left
```

### Initial Planets (Static Reference)

**Field**: `initial_planets`
**Type**: `List[List]`
**Format**: `[[id, owner, x, y, radius, ships, production], ...]`
**Description**: Planet positions and state at the beginning of the game

**Purpose**: Use this to predict where orbiting planets will be in future turns

**Example**:
```python
initial = obs["initial_planets"]
angular_v = obs["angular_velocity"]

# Predict planet position N turns in the future
def predict_position(initial_planet, turns_ahead):
    id_, owner, x, y, radius, ships, production = initial_planet
    
    # Check if planet orbits (distance + radius < 50)
    center_dist = math.hypot(x - 50, y - 50)
    if center_dist + radius < 50:
        # Orbiting planet - rotate around (50, 50)
        new_angle = math.atan2(y - 50, x - 50) + angular_v * turns_ahead
        new_x = 50 + center_dist * math.cos(new_angle)
        new_y = 50 + center_dist * math.sin(new_angle)
        return new_x, new_y
    else:
        # Static planet
        return x, y
```

### Comets Data

**Field**: `comets`
**Type**: `List[Dict]`
**Format**: `[{planet_ids: [...], paths: [...], path_index: [...]}, ...]`

Each comet group dictionary contains:

| Key | Type | Description |
|-----|------|-------------|
| `planet_ids` | List[int] | IDs of the 4 comet planets in this group |
| `paths` | List[List[List[float]]] | Full trajectory for each comet: `[[[x1, y1], [x2, y2], ...], ...]` |
| `path_index` | List[int] | Current position along path for each comet |

**Comet Group Timing**: Spawn at steps 50, 150, 250, 350, 450 (5 groups total, 4 comets per group)

**Example**:
```python
comets = obs["comets"]
if comets:
    group = comets[0]
    planet_ids = group["planet_ids"]  # [42, 43, 44, 45]
    paths = group["paths"]  # [[...path 1...], [...path 2...], ...]
    indices = group["path_index"]  # [15, 15, 15, 15] (position along path)
    
    # Get current position of first comet
    current_idx = indices[0]
    current_pos = paths[0][current_idx]  # [x, y]
    
    # Predict next position
    if current_idx + 1 < len(paths[0]):
        next_pos = paths[0][current_idx + 1]
```

**Field**: `comet_planet_ids`
**Type**: `List[int]`
**Description**: All planet IDs that are currently comets (subset of `planets[i][0]`)

**Example**:
```python
comet_ids = obs["comet_planet_ids"]  # e.g., [42, 43, 44, 45]

# Check if a planet is a comet
planets = obs["planets"]
for planet in planets:
    is_comet = planet[0] in comet_ids
```

## Action Data

Your agent function must return a list of moves to execute each turn.

### Move Format

**Type**: `List[List]`
**Format**: `[[from_planet_id, direction_angle, num_ships], ...]`

Each move is a 3-element array:

| Index | Name | Type | Constraints | Description |
|-------|------|------|-------------|-------------|
| 0 | from_planet_id | int | Must own planet | Source planet ID |
| 1 | direction_angle | float | 0-2π | Direction in radians |
| 2 | num_ships | int | ≤ planet.ships | Number of ships to send |

**Example**:
```python
def agent(obs):
    moves = []
    
    # Move 1: Launch from planet 2 toward angle 0 (right) with 50 ships
    moves.append([2, 0, 50])
    
    # Move 2: Launch from planet 5 toward angle π/2 (down) with 30 ships
    moves.append([5, math.pi/2, 30])
    
    # Move 3: Launch from planet 8 at 45 degrees with 100 ships
    moves.append([8, math.pi/4, 100])
    
    return moves  # Empty list [] is valid (no action)
```

### Angle Convention

Angle is in **radians**, measured from positive X-axis (right):

```
π/2 = 90°  (down)
  ↓
π ← + → 0 (left  right)
  ↑
3π/2 = 270° (up)
```

**Common angles**:
- 0: Right (east)
- π/2: Down (south)
- π: Left (west)
- 3π/2: Up (north)
- π/4: Down-right (southeast)
- 3π/4: Down-left (southwest)
- 5π/4: Up-left (northwest)
- 7π/4: Up-right (northeast)

**Example - Calculate angle to target**:
```python
import math

my_planet = (30, 50)
target = (70, 80)

# Calculate angle
dx = target[0] - my_planet[0]  # 40
dy = target[1] - my_planet[1]  # 30
angle = math.atan2(dy, dx)      # ~0.644 radians (~37°)
```

### Move Constraints & Validation

**Valid move requirements**:
1. `from_planet_id` must exist and be owned by your player
2. `num_ships` must be ≤ planet's current ship count
3. `direction_angle` must be a valid float (0-2π recommended, but any value works)
4. All three fields must be numeric

**Invalid moves** (will be silently ignored or cause error):
```python
# ❌ Launch from planet you don't own
[3, 0, 100]  # if you're player 0 and planet 3 is player 1

# ❌ Launch more ships than available
[5, 0, 150]  # if planet 5 only has 100 ships

# ❌ Non-numeric values
[5, "north", 50]  # angle must be float
[5, 0, 50.5]  # num_ships must be int

# ✓ Valid empty move
[]  # No action this turn
```

## Complete Example: Parsing Observation

```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet
import math

def agent(obs):
    # Parse basic fields
    player_id = obs["player"]
    angular_velocity = obs["angular_velocity"]
    time_budget = obs["remainingOverageTime"]
    
    # Parse planets with named tuple
    planets = [Planet(*p) for p in obs["planets"]]
    
    # Parse fleets with named tuple
    fleets = [Fleet(*f) for f in obs["fleets"]]
    
    # Filter by owner
    my_planets = [p for p in planets if p.owner == player_id]
    enemy_planets = [p for p in planets if p.owner != player_id and p.owner != -1]
    neutral_planets = [p for p in planets if p.owner == -1]
    
    # Get comet information
    comet_ids = obs["comet_planet_ids"]
    my_comet_planets = [p for p in planets if p.id in comet_ids and p.owner == player_id]
    
    # Build moves
    moves = []
    
    for my_planet in my_planets:
        if my_planet.ships < 2:
            continue  # Skip if insufficient ships
        
        # Find nearest neutral planet
        if neutral_planets:
            target = min(neutral_planets, 
                        key=lambda t: math.hypot(my_planet.x - t.x, my_planet.y - t.y))
            
            # Calculate angle and required ships
            angle = math.atan2(target.y - my_planet.y, target.x - my_planet.x)
            ships_needed = target.ships + 1
            
            if my_planet.ships >= ships_needed:
                moves.append([my_planet.id, angle, ships_needed])
    
    return moves
```

## Data Access Patterns

### Pattern 1: Direct Array Access
```python
planets = obs["planets"]
planet_owner = planets[0][1]  # Owner of first planet
planet_ships = planets[0][5]  # Ships on first planet
```

### Pattern 2: Named Tuples
```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
planets = [Planet(*p) for p in obs["planets"]]
planet_owner = planets[0].owner
planet_ships = planets[0].ships
```

### Pattern 3: Dictionary-like Access (if obs is dict-like)
```python
planet_owner = obs.planets[0].owner  # Some wrappers support this
```

## Performance Notes

- **Observation size**: Typically small (< 50 planets, < 100 fleets)
- **Parsing**: Converting to named tuples is cheap and improves readability
- **Computation budget**: 1 second per turn (default), with optional overage
- **Data structure**: Arrays are more efficient than dicts for this use case

## Type Hints (for reference)

```python
from typing import List, Dict, Tuple, Union

# Observation type
Observation = Dict[str, Union[
    List[List[Union[int, float]]],  # planets, fleets, initial_planets
    int,                             # player
    float,                           # angular_velocity, remainingOverageTime
    List[Dict],                      # comets
    List[int]                        # comet_planet_ids
]]

# Action type
Action = List[List[Union[int, float]]]  # List of [planet_id, angle, ships]
```
