# Orbit Wars - Data Utilities & Analysis Patterns

Common patterns and utilities for analyzing game state and making decisions.

## State Analysis Utilities

### Calculate Fleet Speed

```python
import math

def calculate_fleet_speed(num_ships, max_speed=6.0):
    """
    Calculate fleet speed based on number of ships.
    
    Args:
        num_ships: Number of ships in the fleet
        max_speed: Maximum speed (default 6.0)
    
    Returns:
        Speed in units per turn
    """
    if num_ships <= 0:
        return 0
    
    return 1.0 + (max_speed - 1.0) * ((math.log(num_ships) / math.log(1000)) ** 1.5)

# Examples
print(calculate_fleet_speed(1))      # 1.0
print(calculate_fleet_speed(500))    # ~5.0
print(calculate_fleet_speed(1000))   # 6.0
```

### Predict Planet Rotation

```python
import math

def predict_planet_position(initial_planet, angular_velocity, turns_ahead, center=(50, 50)):
    """
    Predict position of a planet after N turns.
    
    Args:
        initial_planet: Initial planet data [id, owner, x, y, radius, ships, production]
        angular_velocity: Rotation speed (radians/turn)
        turns_ahead: Number of turns to predict
        center: Sun center (default (50, 50))
    
    Returns:
        (x, y) tuple of predicted position, or (x, y) original if static
    """
    id_, owner, x, y, radius, ships, production = initial_planet
    
    # Check if planet orbits (distance from center + radius < 50)
    center_dist = math.hypot(x - center[0], y - center[1])
    
    # Planets with orbital_radius + planet_radius >= 50 don't rotate
    if center_dist + radius >= 50:
        return x, y  # Static planet
    
    # Orbiting planet - rotate around center
    current_angle = math.atan2(y - center[1], x - center[0])
    new_angle = current_angle + angular_velocity * turns_ahead
    
    new_x = center[0] + center_dist * math.cos(new_angle)
    new_y = center[1] + center_dist * math.sin(new_angle)
    
    return new_x, new_y

# Example
initial_planets = obs["initial_planets"]
angular_v = obs["angular_velocity"]

# Where will planet 0 be in 10 turns?
future_pos = predict_planet_position(initial_planets[0], angular_v, 10)
print(f"Planet 0 position in 10 turns: {future_pos}")
```

### Predict Comet Position

```python
def predict_comet_position(comet_group, comet_index, turns_ahead):
    """
    Predict comet position after N turns.
    
    Args:
        comet_group: Comet group dict with 'paths' and 'path_index'
        comet_index: Which comet in the group (0-3)
        turns_ahead: Number of turns to predict
    
    Returns:
        (x, y) tuple or None if comet exits board
    """
    path = comet_group["paths"][comet_index]
    current_idx = comet_group["path_index"][comet_index]
    
    future_idx = current_idx + turns_ahead
    
    if future_idx >= len(path):
        return None  # Comet has left the board
    
    x, y = path[future_idx]
    return x, y

# Example
comets = obs["comets"]
if comets:
    group = comets[0]
    future_pos = predict_comet_position(group, 0, 5)
    if future_pos:
        print(f"Comet 0 position in 5 turns: {future_pos}")
    else:
        print("Comet 0 will have left the board")
```

### Calculate Distance & Travel Time

```python
import math

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def travel_time(from_pos, to_pos, num_ships, max_speed=6.0):
    """
    Calculate approximate turns for fleet to travel between positions.
    
    Args:
        from_pos: (x, y) starting position
        to_pos: (x, y) target position
        num_ships: Fleet size
        max_speed: Maximum speed
    
    Returns:
        Approximate turns (does not account for actual collision detection)
    """
    dist = distance(from_pos, to_pos)
    speed = 1.0 + (max_speed - 1.0) * ((math.log(max(num_ships, 1)) / math.log(1000)) ** 1.5)
    
    if speed == 0:
        return float('inf')
    
    return dist / speed

# Example
from_planet = planets[0]
to_planet = planets[1]
travel = travel_time((from_planet.x, from_planet.y), 
                     (to_planet.x, to_planet.y), 
                     100)
print(f"Travel time with 100 ships: {travel} turns")
```

### Check Fleet Collision with Sun

```python
def will_hit_sun(from_pos, to_pos, sun_center=(50, 50), sun_radius=10):
    """
    Check if a fleet's path will collide with the sun.
    
    This is a simple line-circle collision check. The actual game uses
    continuous collision detection, but this gives a reasonable estimate.
    
    Args:
        from_pos: Starting position (x, y)
        to_pos: Target position (x, y)
        sun_center: Sun center
        sun_radius: Sun radius
    
    Returns:
        Boolean indicating if collision occurs
    """
    # Vector from start to end
    fx, fy = from_pos
    tx, ty = to_pos
    dx = tx - fx
    dy = ty - fy
    
    # Vector from start to sun center
    cx, cy = sun_center
    sx = cx - fx
    sy = cy - fy
    
    # Project sun center onto line
    line_len_sq = dx*dx + dy*dy
    if line_len_sq == 0:
        return distance(from_pos, sun_center) <= sun_radius
    
    t = max(0, min(1, (sx*dx + sy*dy) / line_len_sq))
    
    # Closest point on line segment
    closest_x = fx + t * dx
    closest_y = fy + t * dy
    
    dist_to_sun = distance((closest_x, closest_y), sun_center)
    return dist_to_sun <= sun_radius

# Example
will_collide = will_hit_sun((20, 50), (80, 50))
print(f"Will hit sun: {will_collide}")
```

### Check Fleet Collision with Planet

```python
def will_hit_planet(from_pos, to_pos, planet, tolerance=0.1):
    """
    Check if a fleet's path will collide with a planet.
    
    Args:
        from_pos: Starting position
        to_pos: Target position
        planet: Planet object or [id, owner, x, y, radius, ships, production]
        tolerance: Distance tolerance
    
    Returns:
        Boolean indicating collision
    """
    if hasattr(planet, 'x'):  # Named tuple
        px, py, radius = planet.x, planet.y, planet.radius
    else:  # Array
        px, py, radius = planet[2], planet[3], planet[4]
    
    dist_to_center = distance(from_pos, (px, py))
    
    # Simple check: if starting distance > ending distance, moving toward planet
    final_dist = distance(to_pos, (px, py))
    
    # More accurate: point-to-line distance
    fx, fy = from_pos
    tx, ty = to_pos
    cx, cy = px, py
    
    dx = tx - fx
    dy = ty - fy
    
    line_len_sq = dx*dx + dy*dy
    if line_len_sq == 0:
        return distance(from_pos, (px, py)) <= radius + tolerance
    
    t = max(0, min(1, ((cx-fx)*dx + (cy-fy)*dy) / line_len_sq))
    closest_x = fx + t*dx
    closest_y = fy + t*dy
    
    dist = distance((closest_x, closest_y), (px, py))
    return dist <= radius + tolerance
```

## Decision Making Patterns

### Find Nearest Planet

```python
def find_nearest_planet(from_pos, planets, filter_fn=None):
    """
    Find nearest planet, optionally filtering by condition.
    
    Args:
        from_pos: (x, y) reference position
        planets: List of planets
        filter_fn: Optional filter function (e.g., lambda p: p.owner == -1)
    
    Returns:
        Nearest planet or None
    """
    candidates = planets
    if filter_fn:
        candidates = [p for p in planets if filter_fn(p)]
    
    if not candidates:
        return None
    
    return min(candidates, 
              key=lambda p: distance(from_pos, (p.x if hasattr(p, 'x') else p[2],
                                                 p.y if hasattr(p, 'y') else p[3])))

# Example
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet

planets = [Planet(*p) for p in obs["planets"]]
my_planet = planets[0]

# Find nearest neutral planet
target = find_nearest_planet((my_planet.x, my_planet.y), 
                            planets, 
                            filter_fn=lambda p: p.owner == -1)
```

### Calculate Minimum Ships Needed to Capture

```python
def ships_needed_to_capture(target_planet):
    """
    Calculate minimum ships to send to capture a planet.
    
    Args:
        target_planet: Target planet [id, owner, x, y, radius, ships, production]
    
    Returns:
        Minimum ships needed
    """
    return target_planet[5] + 1  # planet.ships + 1

def ships_for_overwhelming_force(target_planet, multiplier=1.5):
    """
    Calculate ships for overwhelming attack (account for reinforcement risk).
    
    Args:
        target_planet: Target planet
        multiplier: Safety multiplier
    
    Returns:
        Recommended ships
    """
    return int(target_planet[5] * multiplier) + 1
```

### Evaluate Planet Value

```python
def planet_value_score(planet, my_pos=None):
    """
    Score planet value for targeting (higher = more valuable).
    
    Considers:
    - Production rate
    - Current garrison (easier to capture if low)
    - Distance (closer is better)
    
    Args:
        planet: Planet data
        my_pos: Optional (x, y) for distance calculation
    
    Returns:
        Value score (higher is better)
    """
    production = planet[6]
    ships = planet[5]
    
    # Production matters (1-5 scale)
    value = production * 10
    
    # Low garrison is better (makes capturing easier)
    value -= ships * 0.5
    
    # Distance penalty if provided
    if my_pos:
        dist = distance(my_pos, (planet[2], planet[3]))
        value -= dist * 0.1
    
    return value
```

### Identify Threats

```python
def find_threatening_fleets(my_planet, fleets, distance_threshold=20):
    """
    Find enemy fleets that could threaten a planet.
    
    Args:
        my_planet: My planet
        fleets: All fleets
        distance_threshold: Alert distance
    
    Returns:
        List of threatening fleets
    """
    threats = []
    
    for fleet in fleets:
        if fleet.owner == my_planet.owner:
            continue  # Friendly fleet
        
        dist = distance((fleet.x, fleet.y), (my_planet.x, my_planet.y))
        
        if dist < distance_threshold:
            threats.append((fleet, dist))
    
    return sorted(threats, key=lambda x: x[1])  # Sorted by distance
```

## Game State Queries

### Count Total Ships

```python
def count_total_ships(player_id, planets, fleets):
    """Count all ships owned by a player (planets + fleets)."""
    planet_ships = sum(p.ships for p in planets if p.owner == player_id)
    fleet_ships = sum(f.ships for f in fleets if f.owner == player_id)
    return planet_ships + fleet_ships

# Example
my_ships = count_total_ships(obs["player"], planets, fleets)
print(f"My total ships: {my_ships}")
```

### List Planets by Status

```python
def analyze_planets(planets, player_id):
    """Categorize planets by ownership and status."""
    owned = [p for p in planets if p.owner == player_id]
    enemy = [p for p in planets if p.owner != player_id and p.owner != -1]
    neutral = [p for p in planets if p.owner == -1]
    
    return {
        "owned": owned,
        "enemy": enemy,
        "neutral": neutral,
        "total_owned_ships": sum(p.ships for p in owned),
        "total_available_ships": sum(p.ships for p in owned if p.ships > 1)
    }

# Example
status = analyze_planets(planets, obs["player"])
print(f"Owned planets: {len(status['owned'])}")
print(f"Available ships: {status['total_available_ships']}")
```

### Estimate Opponent Strength

```python
def estimate_player_strength(player_id, planets, fleets):
    """
    Estimate total strength of a player.
    
    Returns:
        Dictionary with various metrics
    """
    player_planets = [p for p in planets if p.owner == player_id]
    player_fleets = [f for f in fleets if f.owner == player_id]
    
    return {
        "planets": len(player_planets),
        "planet_ships": sum(p.ships for p in player_planets),
        "fleet_ships": sum(f.ships for f in player_fleets),
        "num_fleets": len(player_fleets),
        "total_ships": sum(p.ships for p in player_planets) + 
                      sum(f.ships for f in player_fleets),
        "avg_production": sum(p.production for p in player_planets) / max(1, len(player_planets))
    }
```

## Logging & Debugging

### Format Observation for Logging

```python
def log_game_state(obs, turn):
    """Log current game state for debugging."""
    player = obs["player"]
    planets = [Planet(*p) for p in obs["planets"]]
    fleets = [Fleet(*f) for f in obs["fleets"]]
    
    my_planets = [p for p in planets if p.owner == player]
    my_ships = sum(p.ships for p in my_planets) + sum(f.ships for f in fleets if f.owner == player)
    
    print(f"\n=== TURN {turn} ===")
    print(f"Player {player}: {len(my_planets)} planets, {my_ships} ships")
    print(f"Total planets: {len(planets)}, Total fleets: {len(fleets)}")
    
    for i in range(4):
        strength = estimate_player_strength(i, planets, fleets)
        print(f"  Player {i}: {strength['total_ships']} ships, {strength['planets']} planets")
```

These utilities provide a foundation for more complex agent logic. Combine them for sophisticated decision-making!
