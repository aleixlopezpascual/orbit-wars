# Orbit Wars - Complete Game Rules

## Board Layout

### Dimensions
- **Board Size**: 100x100 continuous space
- **Origin**: Top-left corner (0, 0)

### Sun
- **Position**: Center at (50, 50)
- **Radius**: 10 units
- **Effect**: Fleets crossing the sun are destroyed
- **Symmetry**: All planets and comets use 4-fold mirror symmetry around the center
  - Positions: (x, y), (100-x, y), (x, 100-y), (100-x, 100-y)
  - Ensures fairness regardless of starting position

## Planets

### Representation
`[id, owner, x, y, radius, ships, production]`

- **owner**: Player ID (0-3) or -1 for neutral
- **radius**: Derived from production: `1 + ln(production)`
- **production**: Integer 1-5, generates this many ships per turn
- **ships**: Current garrison (starts 5-99, skewed toward lower values)

### Planet Types

#### Orbiting Planets
- Planets where `orbital_radius + planet_radius < 50`
- Rotate around sun at constant angular velocity
- Angular velocity range: 0.025-0.05 radians/turn (randomized per game)
- **Predictable**: Use `initial_planets` and `angular_velocity` from observation

#### Static Planets
- Planets further from center do not rotate
- Fixed positions throughout the game

### Map Composition
- **Total planets**: 20-40 (5-10 symmetric groups of 4)
- **Guaranteed static**: At least 3 groups
- **Guaranteed orbiting**: At least 1 group

### Home Planets
- One symmetric group randomly chosen as starting planets
- **2-player game**: Players start on diagonally opposite planets (Q1 and Q4) with 10 ships
- **4-player game**: Each player gets one planet from the group with 10 ships

## Fleets

### Representation
`[id, owner, x, y, angle, from_planet_id, ships]`

- **angle**: Direction of travel in radians (0 = right, π/2 = down)
- **ships**: Number of ships (does not change during travel)

### Fleet Speed
Scales logarithmically with size:
```
speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000)) ^ 1.5
```
- 1 ship moves at 1.0 units/turn
- Larger fleets move faster, approaching max speed (default 6.0)
- ~500 ships: ~5 units/turn
- ~1000 ships: 6.0 units/turn (max)

### Fleet Movement
- Travel in straight lines at computed speed each turn
- **Collision detection**: Continuous (entire path segment checked, not just endpoint)
- Fleet is removed if it:
  - Goes out of bounds (leaves 100x100 field)
  - Crosses the sun (path within sun's radius)
  - Collides with any planet (triggers combat)

### Fleet Launch
Each turn, return moves: `[from_planet_id, direction_angle, num_ships]`

Rules:
- Can only launch from planets you own
- Cannot launch more ships than planet has
- Fleet spawns just outside planet's radius in given direction
- Can issue multiple launches from same/different planets per turn

## Comets

### Overview
- Temporary extra-solar objects flying through board on elliptical orbits
- Spawn in groups of 4 (one per quadrant) at steps: 50, 150, 250, 350, 450
- **Radius**: 1.0 (fixed)
- **Production**: 1 ship/turn when owned
- **Speed**: Configurable (default 4.0 units/turn)
- **Starting ships**: Random, skewed low (min of 4 rolls from 1-99)
  - All 4 comets in a group share same starting ship count

### Identification
- Check `comet_planet_ids` in observation to identify comet IDs
- Comets appear in `planets` array, follow all normal planet rules
- Captured, produce ships, can launch fleets from them

### Behavior
- When comet leaves board, it's removed along with garrisoned ships
- Comets removed BEFORE fleet launches each turn
  - Cannot launch from departing comet
- Use `comets` observation field for paths and trajectory prediction
  - Includes `paths` (full trajectory) and `path_index` (current position)

## Turn Order

Each turn executes in this exact order:

1. **Comet Expiration**: Remove comets that left the board
2. **Comet Spawning**: Spawn new comet groups at designated steps (50, 150, 250, 350, 450)
3. **Fleet Launch**: Process all player actions, create new fleets
4. **Production**: All owned planets (including comets) generate ships
5. **Fleet Movement**: Move all fleets along headings
   - Check out-of-bounds, sun collision, planet collision
   - Queue fleets hitting planets for combat
6. **Planet Rotation & Comet Movement**: Orbiting planets rotate, comets advance
   - Any fleet caught by moving planet/comet swept into combat
7. **Combat Resolution**: Resolve all queued combats

## Combat

### Trigger
When one or more fleets collide with a planet:
- By flying into it
- By being swept by a moving planet

### Resolution Rules

1. **Group by attacker owner**: Sum ships from same owner
2. **Largest vs second largest**: These two forces fight
3. **Survivors**: Take difference in ships between them
4. **Outcome if survivors**:
   - If attacker owner = planet owner: surviving ships added to garrison
   - If attacker owner ≠ planet owner:
     - Surviving ships fight garrison
     - If attackers > garrison: planet changes ownership, survivors become new garrison
5. **Tie case**: If two attackers tie exactly, all attacking ships destroyed (no survivors)

## Scoring & Termination

### Game End Conditions
1. Step limit reached: 500 turns
2. Elimination: Only one player (or zero) remains with any planets or fleets

### Final Score
```
Final Score = Total ships on owned planets + Total ships in owned fleets
```
Highest score wins. Ties break by comparing fleet counts, then by Elo rating.

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| episodeSteps | 500 | Maximum number of turns |
| actTimeout | 1 | Seconds per turn |
| shipSpeed | 6.0 | Maximum fleet speed |
| sunRadius | 10.0 | Sun radius |
| boardSize | 100.0 | Board dimensions |
| cometSpeed | 4.0 | Comet speed (units/turn) |
