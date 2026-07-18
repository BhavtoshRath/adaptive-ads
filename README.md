# Adaptive Ads

A simulated ad/item-serving environment where a multi-agent system (researcher,
strategist, executor) learns to personalize item recommendations from simulated
user click and dwell-time behavior — with every decision logged and explainable.

## Status
🚧 In progress — simulator, memory store, and all three agents (researcher,
strategist, executor) are implemented and unit-tested. The eval harness
(`eval/run_eval.py`) that chains them into an end-to-end pipeline and compares
against baselines is not yet implemented.

## Architecture

```
User signals (clicks, dwell time)
        |
        v
Researcher agent  -->  summarizes what's known about the user
        |
        v
Strategist agent  -->  decides what to serve next (uses Memory store)
        |
        v
Executor agent    -->  serves the item, logs the decision
        |
        v
Memory store      <--  updated with the outcome
```

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
