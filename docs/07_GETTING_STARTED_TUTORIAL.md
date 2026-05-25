# Orbit Wars - Getting Started Tutorial

A step-by-step guide to building and testing your first agent.

## Setup

### 1. Install the Environment

```bash
pip install --upgrade "kaggle-environments>=1.28.0"
```

### 2. Create the Environment

```python
from kaggle_environments import make

env = make("orbit_wars", debug=True)
print(f"Environment: {env.name} v{env.version}")
print(f"Players: {env.specification.agents}")
print(f"Max steps: {env.configuration.episodeSteps}")
```

**Output**:
```
Environment: orbit_wars v1.0.9
Players: [2, 4]
Max steps: 500
```

## Understanding the Observation

Each turn, your agent receives an observation dictionary with:

- **player** - Your player ID (0-3)
- **planets** - List of `[id, owner, x, y, radius, ships, production]`
- **fleets** - List of `[id, owner, x, y, angle, from_planet_id, ships]`
- **angular_velocity** - How fast inner planets rotate (radians/turn)

Your agent returns a list of moves: `[from_planet_id, angle_in_radians, num_ships]`

### Exploring an Observation

```python
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet

# Run a quick game to see observations
env = make("orbit_wars", debug=True)
env.run(["random", "random"])

# Get the initial observation
obs = env.steps[1][0].observation  # step 1 = first action step
planets = [Planet(*p) for p in obs.planets]

print(f"Player: {obs.player}")
print(f"Angular velocity: {obs.angular_velocity:.4f} rad/turn")
print(f"\nPlanets ({len(planets)}):")
for p in planets[:6]:
    owner_str = f"Player {p.owner}" if p.owner >= 0 else "Neutral"
    print(f"  id={p.id} owner={owner_str:10s} pos=({p.x:.1f}, {p.y:.1f}) r={p.radius:.1f} ships={p.ships} prod={p.production}")
```

**Example Output**:
```
Player: 0
Angular velocity: 0.0366 rad/turn

Planets (28):
  id=0 owner=Neutral    pos=(97.7, 74.7) r=1.7 ships=34 prod=2
  id=1 owner=Neutral    pos=(2.3, 74.7) r=1.7 ships=34 prod=2
  id=2 owner=Neutral    pos=(97.7, 25.3) r=1.7 ships=34 prod=2
  id=3 owner=Neutral    pos=(2.3, 25.3) r=1.7 ships=34 prod=2
  id=4 owner=Player 0   pos=(73.6, 94.8) r=1.0 ships=10 prod=1
  id=5 owner=Neutral    pos=(26.4, 94.8) r=1.0 ships=29 prod=1
```

## Your First Agent: Nearest Planet Sniper

Let's build a simple agent with a basic strategy:

1. For each planet you own, find the nearest planet you don't own
2. Check if you have enough ships to capture it (need target's ships + 1)
3. Send exactly enough ships to take it

This teaches the fundamentals: reading observations, computing angles, and sending fleets.

### Implementation

```python
import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet

def nearest_planet_sniper(obs):
    moves = []
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    raw_planets = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    planets = [Planet(*p) for p in raw_planets]

    # Separate our planets from targets
    my_planets = [p for p in planets if p.owner == player]
    targets = [p for p in planets if p.owner != player]

    if not targets:
        return moves

    for mine in my_planets:
        # Find the nearest planet we don't own
        nearest = None
        min_dist = float('inf')
        for t in targets:
            dist = math.sqrt((mine.x - t.x)**2 + (mine.y - t.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = t

        if nearest is None:
            continue

        # How many ships do we need? Target's garrison + 1
        ships_needed = max(nearest.ships + 1, 20)

        # Only send if we have enough
        if mine.ships >= ships_needed:
            # Calculate angle from our planet to the target
            angle = math.atan2(nearest.y - mine.y, nearest.x - mine.x)
            moves.append([mine.id, angle, ships_needed])

    return moves
```

### Test Against Random Agent

```python
env = make("orbit_wars", debug=True)
env.run([nearest_planet_sniper, "random"])

final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

env.render(mode="ipython", width=800, height=600)
```

**Output**:
```
Player 0: reward=1, status=DONE
Player 1: reward=-1, status=DONE
```

Great! Your agent won. Now let's see how it does in a 4-player game:

```python
env4 = make("orbit_wars", debug=True)
env4.run([nearest_planet_sniper, nearest_planet_sniper, 
          nearest_planet_sniper, nearest_planet_sniper])

final = env4.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

env4.render(mode="ipython", width=800, height=600)
```

**Output**:
```
Player 0: reward=1, status=DONE
Player 1: reward=-1, status=DONE
Player 2: reward=-1, status=DONE
Player 3: reward=1, status=DONE
```

## Limitations of the Sniper Agent

While the sniper agent is a good starting point, it has several limitations:

### 1. Doesn't Account for Travel Time
The target planet produces ships while your fleet is in transit. By the time your fleet arrives, the target may have more ships than expected, making your attack insufficient.

**Solution**: Calculate travel time and account for production during transit

### 2. Sends Multiple Fleets to Same Target
When multiple planets all target the same nearby planet, their fleets arrive at different times, potentially wasting ships.

**Solution**: Coordinate targeting and consolidate forces

### 3. Ignores the Sun
Fleets aimed through the center of the board (toward 50, 50) may cross the sun and be destroyed.

**Solution**: Check if fleet path crosses the sun before launching

### 4. Poor Resource Management
Planets with no nearby targets hold ships indefinitely instead of consolidating resources.

**Solution**: Send reserves to planets that are actively expanding

## Improvements to Try

### Account for Travel Time

```python
import math

def travel_time(from_pos, to_pos, num_ships):
    """Estimate turns for fleet to travel."""
    dist = math.hypot(to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
    speed = 1.0 + 5.0 * ((math.log(num_ships) / math.log(1000)) ** 1.5)
    return dist / speed

# In your agent:
travel_turns = travel_time((mine.x, mine.y), (nearest.x, nearest.y), ships_needed)
target_garrison_at_arrival = nearest.ships + (nearest.production * travel_turns)
ships_needed = max(int(target_garrison_at_arrival) + 1, 20)
```

### Avoid the Sun

```python
def will_hit_sun(from_pos, to_pos, sun_center=(50, 50), sun_radius=10):
    """Check if fleet path crosses the sun."""
    fx, fy = from_pos
    tx, ty = to_pos
    dx, dy = tx - fx, ty - fy
    
    sx, sy = sun_center[0] - fx, sun_center[1] - fy
    
    line_len_sq = dx*dx + dy*dy
    if line_len_sq == 0:
        return math.hypot(sun_center[0] - fx, sun_center[1] - fy) <= sun_radius
    
    t = max(0, min(1, (sx*dx + sy*dy) / line_len_sq))
    closest_x = fx + t*dx
    closest_y = fy + t*dy
    
    dist = math.hypot(closest_x - sun_center[0], closest_y - sun_center[1])
    return dist <= sun_radius

# In your agent:
if not will_hit_sun((mine.x, mine.y), (nearest.x, nearest.y)):
    # Safe to launch
    moves.append([mine.id, angle, ships_needed])
```

### Consolidate Forces

```python
# Send reserves from planets with excess ships to help attackers
for source in my_planets:
    if source.ships > 100:  # Excess threshold
        # Find a nearby planet to send reinforcements to
        closest_friendly = min(
            [p for p in my_planets if p.id != source.id],
            key=lambda p: math.hypot(p.x - source.x, p.y - source.y)
        )
        angle = math.atan2(closest_friendly.y - source.y, 
                          closest_friendly.x - source.x)
        moves.append([source.id, angle, 50])  # Send some reserves
```

## Creating a Submission File

Create a `main.py` at the root with your agent function:

```python
import math
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet

def agent(obs):
    """Your agent function - returns list of moves."""
    moves = []
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    raw_planets = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    planets = [Planet(*p) for p in raw_planets]

    # Separate our planets from targets
    my_planets = [p for p in planets if p.owner == player]
    targets = [p for p in planets if p.owner != player]

    if not targets:
        return moves

    for mine in my_planets:
        # Find the nearest planet we don't own
        nearest = None
        min_dist = float('inf')
        for t in targets:
            dist = math.sqrt((mine.x - t.x)**2 + (mine.y - t.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = t

        if nearest is None:
            continue

        # How many ships do we need? Target's garrison + 1
        ships_needed = max(nearest.ships + 1, 20)

        # Only send if we have enough
        if mine.ships >= ships_needed:
            # Calculate angle from our planet to the target
            angle = math.atan2(nearest.y - mine.y, nearest.x - mine.x)
            moves.append([mine.id, angle, ships_needed])

    return moves
```

## Submission Methods

You have three options to submit:

### 1. Upload via Browser
Click "Submit Agent" on the competition homepage and upload your `main.py`

### 2. Use Kaggle CLI
```bash
kaggle competitions submit orbit-wars -f main.py -m "Nearest planet sniper v1"
```

See `04_SUBMISSION_GUIDE.md` for detailed CLI instructions.

### 3. Submit via Notebook
Upload a notebook with `main.py` or `submission.tar.gz`

## Next Steps

1. **Test locally** - Experiment with your agent against random and other baselines
2. **Add improvements** - Implement travel time accounting, sun avoidance, force consolidation
3. **Analyze results** - Download episode replays and logs to see what's working
4. **Iterate** - Submit improved versions (up to 5 per day) and track your rating

## Quick Reference

### Key Functions Used
- `math.hypot(dx, dy)` - Calculate distance
- `math.atan2(dy, dx)` - Calculate angle to target
- `math.sqrt(x*x + y*y)` - Alternative distance calculation
- `math.log(x)` - For fleet speed calculations

### Common Patterns
```python
# Distance
dist = math.hypot(planet1.x - planet2.x, planet1.y - planet2.y)

# Angle to target
angle = math.atan2(target.y - source.y, target.x - source.x)

# Filter planets
my_planets = [p for p in planets if p.owner == my_id]
neutral_planets = [p for p in planets if p.owner == -1]

# Find nearest
nearest = min(candidates, key=lambda p: math.hypot(p.x - ref_x, p.y - ref_y))

# Sum ships
total_ships = sum(p.ships for p in planets if p.owner == my_id)
```

## Troubleshooting

**Agent times out?**
- Your calculation takes too long per turn
- Optimize loops or use simpler algorithms

**Agent returns invalid moves?**
- Check that planet_id is an int, angle is a float, ships is an int
- Verify you own the planet you're launching from
- Verify you have enough ships

**Agent crashes?**
- Check for division by zero (e.g., empty planet list)
- Verify data types (planets is a list, not a dict)
- Add try-catch for debugging

**Agent doesn't capture planets?**
- Check your ships_needed calculation
- Verify angle is correct (use atan2 with dy, dx in right order)
- Account for travel time reducing effective garrison

Good luck! 🚀
