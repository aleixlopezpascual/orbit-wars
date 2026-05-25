# Orbit Wars - Agent Interface Specification

## Agent Function Signature

Your agent is a Python function that receives an observation and returns a list of moves.

```python
def agent(obs):
    # obs is a dict-like object
    # return a list of moves (or empty list for no action)
    return moves
```

## Observation Format

The observation is a dictionary with the following fields:

### Fields

| Field | Type | Description |
|-------|------|-------------|
| **planets** | `[[id, owner, x, y, radius, ships, production], ...]` | All planets including comets |
| **fleets** | `[[id, owner, x, y, angle, from_planet_id, ships], ...]` | All active fleets |
| **player** | `int` | Your player ID (0-3) |
| **angular_velocity** | `float` | Planet rotation speed (radians/turn) |
| **initial_planets** | `[[id, owner, x, y, radius, ships, production], ...]` | Planet positions at game start |
| **comets** | `[{planet_ids, paths, path_index}, ...]` | Active comet group data |
| **comet_planet_ids** | `[int, ...]` | Planet IDs that are comets |
| **remainingOverageTime** | `float` | Remaining overage time budget (seconds) |

### Convenience Named Tuples

The module exports named tuples for easier field access:

```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet, CENTER, ROTATION_RADIUS_LIMIT
```

**Planet tuple**:
```python
Planet(id, owner, x, y, radius, ships, production)
```

**Fleet tuple**:
```python
Fleet(id, owner, x, y, angle, from_planet_id, ships)
```

**Constants**:
- `CENTER = (50, 50)` - Sun center position
- `ROTATION_RADIUS_LIMIT = 50` - Distance limit for orbiting planets

### Example Observation Access

```python
def agent(obs):
    planets = [Planet(*p) for p in obs.get("planets", [])]
    fleets = [Fleet(*f) for f in obs.get("fleets", [])]
    player = obs.get("player", 0)
    
    for p in planets:
        print(f"Planet {p.id}: owner={p.owner}, ships={p.ships}, pos=({p.x}, {p.y})")
    
    return []
```

## Action Format

Your agent must return a **list of moves**, where each move is:

```python
[from_planet_id, direction_angle, num_ships]
```

### Move Parameters

- **from_planet_id** (int): ID of a planet you own
- **direction_angle** (float): Angle in radians
  - 0 = right (east)
  - π/2 = down (south)
  - π = left (west)
  - 3π/2 = up (north)
- **num_ships** (int): Number of ships to send

### Move Constraints

- Can only launch from planets you own
- Cannot launch more ships than the planet currently has
- Can issue multiple launches from same or different planets in one turn
- Return empty list `[]` to take no action

### Example Move Construction

```python
import math

def agent(obs):
    planets = [Planet(*p) for p in obs.get("planets", [])]
    player = obs.get("player", 0)
    moves = []
    
    my_planets = [p for p in planets if p.owner == player]
    
    for my_planet in my_planets:
        if my_planet.ships > 0:
            # Send toward angle 0 (right)
            angle = 0
            ships = min(10, my_planet.ships)  # Send at most 10
            moves.append([my_planet.id, angle, ships])
    
    return moves
```

## Timing

- **Time per turn**: 1 second (actTimeout = 1)
- **Overage time**: Budget for particularly complex decisions
- **Remaining overage**: Available in `remainingOverageTime` field

## Common Agent Patterns

### 1. Nearest Target Attack

```python
import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet

def agent(obs):
    moves = []
    player = obs.get("player", 0)
    planets = [Planet(*p) for p in obs.get("planets", [])]
    
    my_planets = [p for p in planets if p.owner == player]
    targets = [p for p in planets if p.owner != player]
    
    if not targets:
        return moves
    
    for mine in my_planets:
        # Find nearest planet we don't own
        nearest = min(targets, key=lambda t: math.hypot(mine.x - t.x, mine.y - t.y))
        
        # Send exactly enough ships to capture it
        ships_needed = nearest.ships + 1
        if mine.ships >= ships_needed:
            angle = math.atan2(nearest.y - mine.y, nearest.x - mine.x)
            moves.append([mine.id, angle, ships_needed])
    
    return moves
```

### 2. Spreading Evenly

```python
def agent(obs):
    planets = [Planet(*p) for p in obs.get("planets", [])]
    player = obs.get("player", 0)
    moves = []
    
    my_planets = [p for p in planets if p.owner == player]
    
    for my_planet in my_planets:
        # Send ships evenly to all neutral planets
        if my_planet.ships > 5:
            ships_per_target = my_planet.ships // (len(planets) - 1)
            for target in planets:
                if target.owner != player and target.id != my_planet.id:
                    angle = math.atan2(target.y - my_planet.y, target.x - my_planet.x)
                    moves.append([my_planet.id, angle, ships_per_target])
    
    return moves
```

## Testing Locally

```python
from kaggle_environments import make

env = make("orbit_wars", configuration={"seed": 42}, debug=True)
env.run(["main.py", "random"])

# View results
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

# Render in notebook
env.render(mode="ipython", width=800, height=600)
```

## Important Notes

- Your agent receives a full view of the board each turn
- Decision time: 1 second per turn (actTimeout)
- Agent must return valid Python object serializable to JSON
- Exceptions in your agent will mark submission as "Error"
