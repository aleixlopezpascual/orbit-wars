"""
rating_system.py — ELO rating and Kaggle calibration for tournament results.

Provides:
  1. ELO rating calculation from 4-player tournament games
  2. Bradley-Terry pair-wise win probability model
  3. Anchor-based calibration (offline ELO → expected Kaggle ELO via linear regression)
  4. Pool metadata configuration (fixed anchors + rotating agents)

Usage in run_tournament.py:
  from scripts.rating_system import RatingSystem, KNOWN_ANCHORS
  
  rs = RatingSystem(known_anchors=KNOWN_ANCHORS)
  ratings = rs.compute_ratings(tournament_results)
  calibrated = rs.calibrate_to_kaggle(ratings)
"""

import json
import math
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple


# ---------------------------------------------------------------------------
# Configuration: Known offline↔Kaggle anchors
# ---------------------------------------------------------------------------

@dataclass
class KnownAnchor:
    """Maps an agent's offline tournament result to its Kaggle ELO."""
    agent_name: str
    offline_elo_estimate: float  # Estimated offline rating
    kaggle_elo: float             # Verified live ELO on Kaggle
    pool_status: str              # "fixed" | "rotating"
    notes: str                    # context

# Populated from BENCHMARK_LOG and verified live submissions
KNOWN_ANCHORS = [
    KnownAnchor(
        agent_name="control_producer",
        offline_elo_estimate=1200.0,  # strong in 4-player local tournaments
        kaggle_elo=1186.3,             # v36 baseline live (submission 53843506)
        pool_status="fixed",
        notes="Primary control baseline; locked architecture (ProducerLiteRuntime)"
    ),
    KnownAnchor(
        agent_name="control_stronger",
        offline_elo_estimate=1100.0,  # typically 2nd locally
        kaggle_elo=981.3,              # public ELO from 2026-06-18
        pool_status="fixed",
        notes="Secondary control; same ProducerLiteRuntime family as Producer"
    ),
    KnownAnchor(
        agent_name="v36_candidate_min_ships",
        offline_elo_estimate=1240.0,  # local rank 1 in tournament
        kaggle_elo=1186.3,             # promoted live; same score as v36 baseline (submission 53843506)
        pool_status="fixed",
        notes="Promoted v36 candidate: min_ships_to_launch 4.0→8.0; matches Producer ELO live"
    ),
    KnownAnchor(
        agent_name="v37_candidate_wave_cap_5",
        offline_elo_estimate=1220.0,  # local rank 1, 61.9% 1st-place
        kaggle_elo=1170.0,             # live Kaggle (submission 53847724); underperformed locally
        pool_status="rotating",
        notes="Wave-cap candidate: max_waves_per_turn 6→5; local→live transfer gap (-50 ELO)"
    ),
]

# Derive calibration fit from known anchors
def _fit_calibration(anchors: List[KnownAnchor]) -> Tuple[float, float]:
    """
    Linear regression: predicted_kaggle_elo = a * offline_elo_estimate + b
    
    With limited anchors (n<5), use a conservative blended approach:
      - Start with least-squares fit
      - Regularize towards slope ≈ 0.95, small offset
      - This prevents over-fitting noise with few data points
    
    Returns (a, b) coefficients.
    """
    fixed = [a for a in anchors if a.pool_status == "fixed"]
    if len(fixed) < 2:
        # Fallback: slight dampening (conservative)
        return 0.95, 0.0
    
    # Simple linear fit: y = a*x + b
    n = len(fixed)
    x_vals = [a.offline_elo_estimate for a in fixed]
    y_vals = [a.kaggle_elo for a in fixed]
    
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    
    numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
    denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.95, 0.0
    
    a_fit = numerator / denominator
    b_fit = y_mean - a_fit * x_mean
    
    # Regularize: blend towards identity mapping (slope=1, intercept≈0)
    # With small n, we don't trust the fit; be conservative
    blend = 0.4 if n < 4 else 0.6
    a = blend * a_fit + (1.0 - blend) * 1.0
    b = blend * b_fit + (1.0 - blend) * 0.0
    
    return a, b


# ---------------------------------------------------------------------------
# ELO Rating System for 4-player games
# ---------------------------------------------------------------------------

class RatingSystem:
    """
    Computes ELO ratings from multi-player tournament results.
    
    ELO update rule for N-player game (N≤4):
      For each player i with rating R_i:
        1. Compute expected score: E_i = 1 / (1 + 10^((avg_R - R_i)/400))
        2. Actual score: S_i = placement_points / max_points_possible
        3. Update: R'_i = R_i + K * (S_i - E_i)
    
    For 4-player (1st=3pts, 2nd=2pts, 3rd=1pt, 4th=0pts):
      - max_points = 3, so S_i ∈ {0, 1/3, 2/3, 1}
      - K factor = 32 (standard)
    """
    
    def __init__(self, k_factor: float = 32.0, known_anchors: Optional[List[KnownAnchor]] = None):
        self.k_factor = k_factor
        self.known_anchors = known_anchors or []
        self.calibration_a, self.calibration_b = _fit_calibration(self.known_anchors)
    
    def compute_ratings(self, tournament_results: Dict) -> Dict[str, float]:
        """
        Compute ELO ratings from tournament results JSON.
        
        Args:
            tournament_results: Dict with keys:
              - test_agent: str (name of agent being tested)
              - n_agents: int
              - games: list of dicts {combo, names, points, ranks, error, ...}
        
        Returns:
            {agent_name: final_elo, ...}
        """
        n_agents = tournament_results.get("n_agents", 0)
        games = tournament_results.get("games", [])
        
        # Initialize ratings to 1000
        ratings = {}
        for game in games:
            for name in game.get("names", []):
                if name not in ratings:
                    ratings[name] = 1000.0
        
        # Process each game sequentially
        for game in games:
            if game.get("error"):
                continue
            
            names = game["names"]
            points = game["points"]
            
            if not names or not points or len(names) != len(points):
                continue
            
            # Compute new ratings for all players in this game
            new_ratings = self._update_game_ratings(
                names, points, ratings
            )
            
            for name, new_elo in new_ratings.items():
                ratings[name] = new_elo
        
        return ratings
    
    def _update_game_ratings(self, names: List[str], points: List[float], 
                             ratings: Dict[str, float]) -> Dict[str, float]:
        """Update ratings after one 4-player game."""
        n = len(names)
        max_points = 3.0  # for 4-player: 1st=3, 2nd=2, 3rd=1, 4th=0
        
        updated = {}
        
        # Compute average rating (exclude current player)
        avg_rating = sum(ratings.get(names[i], 1000.0) for i in range(n)) / n
        
        for i, name in enumerate(names):
            current_elo = ratings.get(name, 1000.0)
            actual_points = points[i]
            
            # Expected score based on ELO difference
            expected = 1.0 / (1.0 + 10.0 ** ((avg_rating - current_elo) / 400.0))
            
            # Actual score (normalized to [0, 1])
            actual_score = actual_points / max_points
            
            # ELO update
            new_elo = current_elo + self.k_factor * (actual_score - expected)
            updated[name] = new_elo
        
        return updated
    
    def calibrate_to_kaggle(self, offline_ratings: Dict[str, float]) -> Dict[str, Dict]:
        """
        Map offline ELO ratings to predicted Kaggle ELO using known anchors.
        
        Returns:
            {agent_name: {
              "offline_elo": float,
              "predicted_kaggle_elo": float,
              "calibration_confidence": str ("high" | "medium" | "low")
            }, ...}
        """
        result = {}
        
        for agent, offline_elo in offline_ratings.items():
            predicted_kaggle = (
                self.calibration_a * offline_elo + self.calibration_b
            )
            
            # Confidence heuristic: how close to nearest known anchor?
            confidence = "low"
            if self.known_anchors:
                min_dist = min(
                    abs(offline_elo - a.offline_elo_estimate)
                    for a in self.known_anchors
                )
                if min_dist < 50:
                    confidence = "high"
                elif min_dist < 100:
                    confidence = "medium"
            
            result[agent] = {
                "offline_elo": round(offline_elo, 1),
                "predicted_kaggle_elo": round(predicted_kaggle, 1),
                "calibration_confidence": confidence,
            }
        
        return result
    
    def explain_calibration(self) -> str:
        """Return human-readable calibration explanation."""
        lines = [
            "ELO Calibration Model",
            "=" * 60,
            f"Formula: predicted_kaggle_elo = {self.calibration_a:.3f} * offline_elo + {self.calibration_b:.1f}",
            "",
            "Fitted on known anchors (fixed pool agents):",
        ]
        
        for anchor in self.known_anchors:
            if anchor.pool_status == "fixed":
                predicted = (
                    self.calibration_a * anchor.offline_elo_estimate + self.calibration_b
                )
                error = predicted - anchor.kaggle_elo
                lines.append(
                    f"  {anchor.agent_name}: "
                    f"offline={anchor.offline_elo_estimate:.0f} → "
                    f"actual_kaggle={anchor.kaggle_elo:.1f} "
                    f"(predicted={predicted:.1f}, error={error:+.1f})"
                )
        
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Bradley-Terry Pair-wise Model (optional, for future enhancements)
# ---------------------------------------------------------------------------

def bradley_terry_win_probability(rating_a: float, rating_b: float) -> float:
    """
    Bradley-Terry model: P(A beats B) = r_a / (r_a + r_b)
    
    where ratings are interpreted as strength parameters.
    """
    if rating_a + rating_b == 0:
        return 0.5
    return rating_a / (rating_a + rating_b)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def pool_status_summary(anchors: List[KnownAnchor]) -> Dict[str, List[str]]:
    """Summarize pool membership by status."""
    fixed = [a.agent_name for a in anchors if a.pool_status == "fixed"]
    rotating = [a.agent_name for a in anchors if a.pool_status == "rotating"]
    return {
        "fixed_anchors": fixed,
        "rotating_agents": rotating,
    }


if __name__ == "__main__":
    # Demo: show calibration model
    rs = RatingSystem(known_anchors=KNOWN_ANCHORS)
    print(rs.explain_calibration())
    print()
    print("Pool Status:")
    for status, agents in pool_status_summary(KNOWN_ANCHORS).items():
        print(f"  {status}: {agents}")
