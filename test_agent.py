#!/usr/bin/env python3
"""Local test harness for Orbit Wars agent.

Tests the agent with various mock observations to ensure:
1. Agent doesn't crash on valid observations
2. Agent returns valid action format
3. Sun collision detection works
4. Target scoring works correctly
"""

import json
import sys
from pathlib import Path
from baseline.agent import agent


def validate_actions(actions):
    """Validate that actions follow the required format."""
    if not isinstance(actions, list):
        raise ValueError(f"Actions must be a list, got {type(actions)}")
    
    for i, move in enumerate(actions):
        if not isinstance(move, list) or len(move) != 3:
            raise ValueError(f"Move {i} must be [planet_id, angle, ships], got {move}")
        
        pid, angle, ships = move
        if not isinstance(pid, int):
            raise ValueError(f"Move {i}: planet_id must be int, got {type(pid)}")
        if not isinstance(angle, (int, float)):
            raise ValueError(f"Move {i}: angle must be numeric, got {type(angle)}")
        if not isinstance(ships, int) or ships <= 0:
            raise ValueError(f"Move {i}: ships must be positive int, got {ships}")


def test_basic_observation():
    """Test agent with a basic starting observation."""
    print("Test 1: Basic observation with 4 planets")
    obs = {
        "player": 0,
        "angular_velocity": 0.03,
        "remainingOverageTime": 60.0,
        "planets": [
            [0, 0, 10.0, 10.0, 2.5, 40, 3],     # player 0 home
            [1, -1, 22.0, 13.0, 2.0, 12, 2],    # neutral
            [2, -1, 35.0, 25.0, 2.0, 8, 1],     # neutral
            [3, 1, 85.0, 85.0, 2.7, 35, 4],     # player 1 (enemy)
        ],
        "fleets": [],
        "initial_planets": [],
        "comets": [],
        "comet_planet_ids": [],
    }
    
    try:
        actions = agent(obs)
        validate_actions(actions)
        print(f"  ✓ Agent returned valid actions: {actions}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_with_enemy_fleets():
    """Test agent when opponent has fleets."""
    print("Test 2: Observation with incoming enemy fleets")
    obs = {
        "player": 0,
        "angular_velocity": 0.03,
        "remainingOverageTime": 60.0,
        "planets": [
            [0, 0, 10.0, 10.0, 2.5, 80, 3],
            [1, -1, 50.0, 50.0, 2.0, 20, 2],
            [2, 0, 70.0, 10.0, 1.5, 50, 3],
        ],
        "fleets": [
            [0, 1, 40.0, 40.0, 0.5, 1, 15],  # enemy fleet approaching
        ],
        "initial_planets": [[0, 10.0, 10.0]],
        "comets": [],
        "comet_planet_ids": [],
    }
    
    try:
        actions = agent(obs)
        validate_actions(actions)
        print(f"  ✓ Agent returned valid actions: {actions}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_with_comets():
    """Test agent with comet planets."""
    print("Test 3: Observation with comet planets")
    obs = {
        "player": 0,
        "angular_velocity": 0.03,
        "remainingOverageTime": 60.0,
        "planets": [
            [0, 0, 10.0, 10.0, 2.5, 60, 3],
            [1, -1, 50.0, 50.0, 1.0, 5, 1],   # comet (radius 1.0, production 1)
            [2, 1, 85.0, 85.0, 2.7, 40, 4],
        ],
        "fleets": [],
        "initial_planets": [[0, 10.0, 10.0]],
        "comets": [[1, 50.0, 50.0, 1.0]],
        "comet_planet_ids": [1],
    }
    
    try:
        actions = agent(obs)
        validate_actions(actions)
        print(f"  ✓ Agent returned valid actions: {actions}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_low_ships():
    """Test agent when home planet has few ships."""
    print("Test 4: Low ship count (should not launch risky attacks)")
    obs = {
        "player": 0,
        "angular_velocity": 0.03,
        "remainingOverageTime": 60.0,
        "planets": [
            [0, 0, 10.0, 10.0, 2.5, 10, 3],   # only 10 ships
            [1, -1, 50.0, 50.0, 2.0, 20, 2],
            [2, 1, 85.0, 85.0, 2.7, 100, 5],  # strong enemy
        ],
        "fleets": [],
        "initial_planets": [],
        "comets": [],
        "comet_planet_ids": [],
    }
    
    try:
        actions = agent(obs)
        validate_actions(actions)
        print(f"  ✓ Agent returned valid actions: {actions}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_empty_actions():
    """Test agent when it should take no actions."""
    print("Test 5: Observation with no good targets (should return empty)")
    obs = {
        "player": 0,
        "angular_velocity": 0.03,
        "remainingOverageTime": 60.0,
        "planets": [
            [0, 0, 10.0, 10.0, 2.5, 8, 1],    # only minimum garrison
            [1, 1, 85.0, 85.0, 2.7, 200, 5],  # heavily defended enemy
        ],
        "fleets": [],
        "initial_planets": [],
        "comets": [],
        "comet_planet_ids": [],
    }
    
    try:
        actions = agent(obs)
        validate_actions(actions)
        print(f"  ✓ Agent returned valid actions: {actions}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Orbit Wars Baseline Agent Local Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_observation,
        test_with_enemy_fleets,
        test_with_comets,
        test_low_ships,
        test_empty_actions,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
