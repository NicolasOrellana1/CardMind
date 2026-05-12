# CardMind

**CardMind** is a blackjack learning and decision-training platform that teaches you how to play correctly, count cards, and understand exactly *why* each decision is the right one.

Whether you're a complete beginner or someone who has played for years, CardMind gives you instant, honest feedback on every hand — not just "wrong", but *why* it was wrong and what the math says you should have done instead.

---

## What does it actually do?

Most blackjack trainers just flash a red screen when you make a mistake. CardMind goes further:

- It deals hands from a realistic **six-deck shoe**, just like a real casino table.
- It tracks the **Hi-Lo running count and true count** as every card is revealed.
- After each decision, a built-in **Strategy Advisor** tells you the optimal action based on both basic strategy and count-based index deviations (the Illustrious 18).
- It tells you **how much to bet** based on your current true count and the size of your bankroll.
- You can run it as a **CLI simulator** for rapid hands, or open the **browser trainer** for a visual, card-by-card practice session.

---

## Phase 1 Features

| Feature | Status |
|---|---|
| Configurable six-deck shoe (penetration, reshuffle) | Done |
| Hi-Lo running count + true count | Done |
| All legal actions: Hit, Stand, Double, Split, Surrender, Insurance | Done |
| Basic strategy advisor (hard totals, soft totals, pairs) | Done |
| Count deviation advisor (Illustrious 18 index plays) | Done |
| Bet sizing suggestions from true count | Done |
| Interactive CLI (`--interactive`) | Done |
| Batch simulation CLI (`--hands N`) | Done |
| Browser trainer UI (static HTML/CSS/JS) | Done |
| Unit tests for the engine | Done |

---

## Getting Started

### Prerequisites

- Python 3.11 or newer

No other dependencies are required for Phase 1 — the engine and CLI run on the standard library.

### Installation

Clone the repository and you are ready to go:

```bash
git clone https://github.com/NicolasOrellana1/CardMind.git
cd CardMind
```

---

## Running the CLI

### Interactive mode — play hands yourself

Deal cards, make decisions, and get instant advisor feedback after each action:

```bash
python -m cardmind.cli --interactive
```

Example output:

```
--- Hand 1 ---
Player: [8 of Hearts, 5 of Clubs] = 13
Dealer upcard: 6 of Diamonds

Your action (hit/stand/double/surrender): stand
Advisor: STAND — Basic strategy: stand on 13 vs dealer 6.
Result: +1.0 units  |  RC: +2  TC: +0.4
```

### Batch simulation mode — run many hands automatically

Let the built-in strategy advisor play thousands of hands and see the results:

```bash
python -m cardmind.cli --hands 1000
```

You can also seed the simulation for reproducible results:

```bash
python -m cardmind.cli --hands 500 --seed 42
```

---

## Opening the Browser Trainer

The browser UI is a fully static page — no server needed. Just open the file in any browser:

```
web/index.html
```

The trainer shows:

- **Dealer and player cards** rendered on a felt table
- **Running count and true count** updating after each card
- **Suggested bet size** in units based on the current count
- **Bankroll tracker** across the session
- A **live Strategy Advisor panel** that explains each recommended action in plain English
- A **Hi-Lo count reference strip** so you can practice counting mentally before checking

---

## Running the Tests

```bash
python -m pytest
```

Or with the standard library runner:

```bash
python -m unittest discover -s tests
```

---

## How Card Counting Works (Quick Primer)

CardMind uses the **Hi-Lo system**, the most widely taught and battle-tested card counting method.

Every card that comes out of the shoe adjusts the running count:

| Cards | Count Change |
|---|---|
| 2, 3, 4, 5, 6 | +1 (good for the player) |
| 7, 8, 9 | 0 (neutral) |
| 10, J, Q, K, A | -1 (good for the dealer) |

A high positive count means the remaining shoe is rich in tens and aces, which favors the player. The **true count** normalizes this for the number of decks still in the shoe:

```
True Count = Running Count / Decks Remaining
```

CardMind uses the true count to:
- Adjust the recommended action (index deviations like the Illustrious 18)
- Suggest how many betting units to put out

---

## Project Structure

```
CardMind/
├── cardmind/               # Core Python package
│   ├── engine.py           # Game engine, rules, round flow
│   ├── strategy.py         # Basic strategy + count deviations advisor
│   ├── shoe.py             # Six-deck shoe, Hi-Lo count tracking
│   ├── hand.py             # Hand evaluation, soft/hard totals, blackjack
│   ├── cards.py            # Card and deck definitions
│   ├── actions.py          # Action enum (Hit, Stand, Double, etc.)
│   ├── simulator.py        # Batch simulation runner
│   └── cli.py              # Command-line interface
├── web/                    # Browser trainer (static, no build step)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_engine.py
├── pyproject.toml
└── PROJECT_PLAN.md         # Full architecture and roadmap document
```

---

## Roadmap

CardMind is being built in stages. Phase 1 (the engine, advisor, CLI, and browser prototype) is complete. Here is what comes next:

| Phase | What it adds |
|---|---|
| **Phase 2 — Web Teacher** | FastAPI backend + React frontend with drills, progress tracking, EV feedback, and count-speed charts |
| **Phase 3 — Model Training** | Synthetic hand dataset generation, supervised baseline policy, DQN reinforcement learning loop |
| **Phase 4 — Vision Module** | Screen capture pipeline, card detection, rank/suit recognition, live count from any blackjack UI |
| **Phase 5 — Polished Demo** | Docker Compose, session replay, model evaluation dashboard, public deployment |

---

## A Note on Responsible Use

CardMind is an educational and research tool. It is designed for:

- Learning optimal blackjack strategy and card counting in a safe, offline environment
- Building and evaluating blackjack AI/RL models
- Academic study of advantage play and expected value

Using external decision assistance on real-money casino sites is prohibited by those platforms. CardMind is not designed for, and should not be used for, covert live-site assistance.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Engine & CLI | Python 3.11+ (standard library only for Phase 1) |
| Browser Trainer | Vanilla HTML / CSS / JavaScript |
| API (Phase 2) | FastAPI + Pydantic |
| Frontend (Phase 2) | React + Vite + Tailwind CSS |
| ML/RL (Phase 3) | PyTorch, NumPy, Pandas |
| Vision (Phase 4) | OpenCV, Ultralytics YOLO |

---

## Contributing

Contributions are welcome. If you find a rules bug, a strategy table error, or want to add a new drill — open an issue or a pull request.

If you're not sure where to start, the best entry point is [cardmind/strategy.py](cardmind/strategy.py) for strategy logic and [tests/test_engine.py](tests/test_engine.py) for examples of how the engine is tested.

---

## License

MIT — free to use, fork, and build on.
