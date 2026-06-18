# Orbit Wars - Submission & Testing Guide

## Prerequisites

### 1. Install Kaggle CLI

```bash
pip install kaggle
```

### 2. Set Up API Authentication

You'll need a Kaggle account. Sign up at https://www.kaggle.com if needed.

#### Recommended: API Token File

1. Go to https://www.kaggle.com/settings/api
2. Click "Generate New Token" under the "API" section
3. Save to `~/.kaggle/access_token`:

```bash
mkdir -p ~/.kaggle
nano ~/.kaggle/access_token
# Paste the token string
chmod 600 ~/.kaggle/access_token
```

#### Alternative Methods

- **OAuth (browser flow)**: `kaggle auth login`
- **Environment variable**: `export KAGGLE_API_TOKEN=xxxxxxxxxxxxxx`

### 3. Verify CLI Setup

```bash
kaggle competitions list -s "orbit wars"
```

## Joining the Competition

### 1. Accept Rules on Kaggle Website

Navigate to https://www.kaggle.com/competitions/orbit-wars and click "Join Competition"

### 2. Verify Enrollment

```bash
kaggle competitions list --group entered
```

You should see "orbit-wars" in the list.

## Downloading Data

```bash
kaggle competitions download orbit-wars -p orbit-wars-data
```

This downloads starter kits and any provided data files.

## Local Testing

> **Python environment note:** `orbit_wars` is only registered in project virtualenvs, not system Python.
> Use this workspace venv for local validation:
> ```bash
> VENV=.venv/bin/python3
> ```

### Head-to-Head Validation (recommended)

```bash
# Sanity: confirm Producer (1180) beats Stronger (981)
$VENV run_validation.py --ch control_producer.py --bl control_stronger.py -n 4 --seed 42

# Benchmark a new candidate against the PRIMARY control
$VENV run_validation.py --ch <candidate>.py --bl control_producer.py -n 24 --seed 42
```

### Test Your Agent Locally

```python
from kaggle_environments import make

# Single test
env = make("orbit_wars", configuration={"seed": 42}, debug=True)
env.run(["main.py", "random"])

# View result
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")
```

### Run in Command Line

```bash
python -c "
from kaggle_environments import make
env = make('orbit_wars', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"
```

### Render in Notebook

```python
env.render(mode="ipython", width=800, height=600)
```

## External Local Benchmark Framework (Optional)

For richer local benchmarking/visual analysis, you can also use:

- `automatylicza/orbit-wars-lab` — https://github.com/automatylicza/orbit-wars-lab

Use it for tournament visualization, replay inspection, and broader baseline comparisons.  
Competition submission gating in this repository still uses `run_tournament.py` and the policy below.

## Submission Requirements

### File Structure

Your submission must have **main.py** at the root with an `agent` function.

### Mandatory Offline Tournament Check (Before Every Submission)

Every candidate must be evaluated with the offline tournament system before pushing to Kaggle.

```bash
# Required gate runner (executes setup + tournament and validates artifact)
bash scripts/pre_submission_tournament_gate.sh <candidate_agent.py>
```

Expected tournament setup:
- Up to 10 agents total: candidate + prioritized local controls/baselines + Kaggle public agents
- The default priority pool now includes `control_producer.py` and `control_stronger.py`
- 4-player round-robin combinations (210 games when all 10 are present)
- Results saved in `artifacts/tournament_<timestamp>.json`

Fallback rule:
- If Kaggle public agents are temporarily unavailable, run fallback tournament with 50+ games and record the reason in `docs/operations/BENCHMARK_LOG.md`.

No Kaggle submission should be sent without:
1. A fresh passing artifact in `artifacts/tournament_<timestamp>.json` for the same candidate file.
2. A benchmark log entry in `docs/operations/BENCHMARK_LOG.md`.

### Single File Submission

```bash
kaggle competitions submit orbit-wars -f main.py -m "Nearest planet sniper v1"
```

### Multi-File Submission

Bundle files into tar.gz with main.py at root:

```bash
tar -czf submission.tar.gz main.py helper.py model_weights.pkl
kaggle competitions submit orbit-wars -f submission.tar.gz -m "Multi-file agent v1"
```

### Notebook Submission

```bash
kaggle competitions submit orbit-wars -k YOUR_USERNAME/orbit-wars-agent -f submission.tar.gz -v 1 -m "Notebook agent v1"
```

## Monitoring Submissions

### Check Submission Status

```bash
kaggle competitions submissions orbit-wars
```

Each submission will show:
- Status: Pending, InProgress, Completed, or Error
- Skill rating (μ and σ)
- Number of episodes played

### List Episodes

Once your submission has played games:

```bash
kaggle competitions episodes <SUBMISSION_ID>
```

CSV output for scripting:

```bash
kaggle competitions episodes <SUBMISSION_ID> -v
```

### Download Replays

Download replay JSON for an episode (for visualization/analysis):

```bash
kaggle competitions replay <EPISODE_ID>
kaggle competitions replay <EPISODE_ID> -p ./replays
```

### Download Logs

Debug your agent by downloading logs:

```bash
# Logs for first agent (index 0)
kaggle competitions logs <EPISODE_ID> 0

# Logs for second agent (index 1)
kaggle competitions logs <EPISODE_ID> 1 -p ./logs
```

### Check Leaderboard

```bash
kaggle competitions leaderboard orbit-wars -s
```

The `-s` flag shows short format with just rank, team name, and score.

## Submission Constraints

- **Max submissions per day**: 5 agents per team
- **Tracked**: Only latest 2 submissions tracked for final ranking
- **Visible**: Only your best scoring bot shown on leaderboard
- **Initial rating**: New submissions start with μ₀ = 600

## Typical Development Workflow

### 1. Develop Locally

```bash
# Test implementation
python -c "
from kaggle_environments import make
env = make('orbit_wars', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"
```

### 2. Submit to Kaggle

```bash
kaggle competitions submit orbit-wars -f main.py -m "v1"
```

### 3. Monitor Results

```bash
# Check submissions
kaggle competitions submissions orbit-wars

# Check leaderboard
kaggle competitions leaderboard orbit-wars -s
```

### 4. Review Episodes

```bash
# List recent episodes
kaggle competitions episodes <SUBMISSION_ID>

# Download specific episode replay
kaggle competitions replay <EPISODE_ID>

# Download agent logs
kaggle competitions logs <EPISODE_ID> 0
```

### 5. Analyze and Iterate

- Review replays to understand matchups
- Check logs for crashes or logic errors
- Improve strategy based on results
- Submit improved version (up to 5 per day)

## Key Points

- **Validation**: First game validates your agent (plays against itself)
- **Error handling**: If validation fails, download logs to debug
- **Rating convergence**: Newer agents play more frequently initially
- **Best shown**: Leaderboard shows only your highest-rated submission
- **Deadline**: Final submissions accepted until June 23, 2026
