# 15) Why Cloning the #1 Bot Loses to Greedy

Source notebook: https://www.kaggle.com/code/souldrive/why-cloning-the-1-bot-loses-to-greedy

## Why this notebook matters

This notebook is a useful negative result: it shows that cloning the strongest public bot with supervised learning can still lose badly to a simple greedy heuristic.

The reported setup:

- built a large replay-derived dataset (270k+ states)
- trained a sizable model (~2.4M parameters)
- achieved only ~17% win rate against the public greedy baseline ("Producer")
- got worse after PPO fine-tuning (~4% win rate)

## Main learnings

1. **Behavior cloning is easy to scale, but hard to turn into strategy.**  
   You can extract lots of state/action pairs from replays, but the model only learns the observed move, not the search or reasoning that produced it.

2. **Strong bots may depend on planning, not just patterns.**  
   If the teacher relies on lookahead, simulation, or hidden heuristics, a clone usually misses the decision process that made those actions good.

3. **More data and bigger models do not guarantee better gameplay.**  
   Better imitation loss does not necessarily translate into stronger matches against a live opponent.

4. **Post-hoc RL can make an imitation policy worse.**  
   Fine-tuning a weak clone with PPO did not recover the missing strategic structure.

5. **Simple greedy baselines can still beat learned clones.**  
   In Orbit Wars, a hand-built heuristic with the right geometry and mission logic can outperform a large end-to-end model.

## Orbit Wars implications

- Treat replay data as a source of **intent signals**, not a full solution.
- Prefer **hybrid systems**: learned intent prediction + rule-based geometry/safety.
- Use `orbit_lite` or other deterministic logic for angle selection, ship sizing, and collision safety.
- Benchmark against greedy controls early; if the clone loses there, the policy is not strategically ready.

## Practical takeaway

If a top agent is mostly search- or heuristic-driven, pure cloning is usually the wrong first move. The better path is to distill **what to do** from data while keeping **how to execute** in deterministic code.

## Follow-up idea

This notebook supports the backlog item for a per-planet behavioral cloning hybrid: small supervised intent heads, no-op downsampling, and rule-based execution for the actual move generation.
