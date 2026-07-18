# Adaptive Ads

A simulated ad/item-serving environment where a multi-agent system (researcher,
strategist, executor) learns to personalize item recommendations from simulated
user click and dwell-time behavior — with every decision logged and explainable.

## Status
🚧 In progress — simulator, memory store, all three agents (researcher,
strategist, executor), and the eval harness (`eval/run_eval.py`, with random
and most-popular baselines) are implemented and unit-tested.

## Architecture

![Architecture diagram](architecture.png)

## Project structure

- `simulator/` — generates synthetic users, item catalog, and simulated impressions
- `agents/` — researcher, strategist, and executor agents
- `memory/` — SQLite-backed episodic + long-term memory store
- `eval/` — compares the agent pipeline's click-through rate against baselines
- `tests/` — unit tests

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the evaluation

```bash
python eval/run_eval.py
```
