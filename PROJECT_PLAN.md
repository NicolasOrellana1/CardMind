# CardMind Project Plan

CardMind is a two-module blackjack AI project:

1. A card-counting and decision-teaching platform trained/evaluated against realistic blackjack simulations.
2. A vision/perception module that can read a blackjack screen in real time for practice, review, and simulation support.

The safest and most useful first version should target educational play, local simulators, recorded hands, or a controlled demo table. Real-money casino sites commonly prohibit automated or external decision assistance, so the product should avoid stealth/covert live-site use and make the practice/research boundary explicit.

## Product Modules

### Module A: Counter + Decision Teacher

Goal: teach the user optimal blackjack decisions, Hi-Lo counting, true-count conversion, bet ramping, and index deviations.

Core features:

- Blackjack rules engine with configurable table rules.
- Shoe simulation with running count, true count, penetration, reshuffle, splits, doubles, surrender, insurance, and bankroll tracking.
- Strategy engine that can provide:
  - Basic strategy decisions.
  - Count-adjusted deviations such as Illustrious 18.
  - Expected value feedback for each decision.
  - Bet sizing suggestions based on true count and bankroll/risk constraints.
- Training mode with drills:
  - Card value recognition.
  - Running count sequences.
  - True count conversion.
  - Full-hand play while maintaining count.
  - Index deviation practice.
- Model layer:
  - Start with deterministic basic strategy and count rules as the ground truth.
  - Add Monte Carlo simulation for EV estimates.
  - Add RL after the environment is validated.

Recommended first implementation:

- Build a correct simulator first.
- Use basic strategy plus Hi-Lo/index tables as a transparent baseline.
- Generate synthetic training data from the simulator instead of relying on scarce public blackjack hand datasets.
- Train ML/RL models only after the simulator passes rule and EV sanity tests.

### Module B: Screen Perception Assistant

Goal: detect visible cards and table state from a controlled blackjack UI or recording, then feed that state into Module A.

Core features:

- Screen capture pipeline.
- Card region detection.
- Rank/suit recognition.
- Dealer/player hand grouping.
- State reconciliation across frames so the same card is not counted repeatedly.
- Confidence scoring and manual correction UI.
- Integration with decision engine.

Recommended first implementation:

- Start with a local demo blackjack table where card positions are predictable.
- Add image/OCR recognition for standard card assets.
- Move to YOLO/RT-DETR style object detection only after enough labeled screenshots exist.
- Store every recognized frame and correction so the dataset improves over time.

## Architecture

```text
apps/
  web/                  React app: trainer, dashboard, drills, live practice UI
  api/                  FastAPI app: sessions, decisions, metrics, websocket state
packages/
  blackjack_engine/     Rules engine, shoe, hand evaluation, strategy tables
  card_vision/          Screen capture, detection, OCR/classification, frame state
  ml/                   RL training, model inference, evaluation scripts
  shared/               Shared schemas and fixtures
data/
  raw/                  Captured screenshots, hand logs, external datasets
  processed/            Labeled cards, generated hands, training splits
models/
  policy/               Decision models
  betting/              Bet sizing models
  vision/               Card detector/classifier models
docs/
  rules.md              Supported blackjack rule variants
  evaluation.md         Accuracy, EV, and model validation methodology
```

## Training/Data Strategy

Public blackjack datasets are not the main bottleneck. Blackjack is easier to simulate than to scrape: a correct environment can generate millions of labeled hands with known counts, legal actions, outcomes, and EV estimates.

Useful datasets to create internally:

- `hands.parquet`: generated simulated hands with state, action, reward, count, and outcome.
- `strategy_labels.parquet`: basic strategy and count-deviation labels.
- `ev_samples.parquet`: Monte Carlo EV estimates for state/action pairs.
- `screenshots/`: captured table screenshots with bounding boxes and card labels.
- `frame_events.parquet`: recognized card appearances over time for count reconciliation.

Model sequence:

1. Rule baseline: basic strategy + Hi-Lo + index deviations.
2. EV simulator: Monte Carlo estimates for action comparison.
3. Supervised policy model: imitate baseline/EV labels.
4. RL policy model: train inside validated simulator.
5. Betting model: learn or fit a risk-controlled bet ramp from true count.
6. Vision model: card detector/classifier trained on captured/labeled table images.

## MVP Phases

### Phase 1: Engine + CLI

- Implement blackjack engine.
- Support realistic shoe and table rules.
- Add deterministic strategy advisor.
- Add CLI simulation runner.
- Add unit tests for hand values, legal actions, count updates, reshuffle, and payouts.

### Phase 2: Web Teacher

- Build FastAPI decision endpoint.
- Build React trainer with hand display, count tracker, and decision feedback.
- Add drills and persistent progress.
- Add charts for accuracy, EV, and counting speed.

### Phase 3: Model Training

- Generate synthetic hand dataset.
- Train supervised baseline policy.
- Add DQN training loop.
- Compare model decisions to basic strategy and EV simulation.
- Export models for inference.

### Phase 4: Vision Practice Mode

- Build screen capture for a controlled local blackjack simulator.
- Detect card locations and classify ranks/suits.
- Add frame-to-frame card memory to prevent double-counting.
- Surface confidence and allow manual correction.
- Feed recognized state into the teacher.

### Phase 5: Polished Demo

- Docker Compose for API, web, Redis, and optional trainer worker.
- Replay mode with saved sessions.
- Model evaluation dashboard.
- Deployment configuration for a public demo.

## Key Technical Risks

- Blackjack rule correctness is easy to underestimate. The simulator must be tested before any model training matters.
- RL can learn artifacts from a flawed environment. Use basic strategy and Monte Carlo EV checks as guardrails.
- Screen recognition fails when table themes, animations, scaling, or compression change. Start with one controlled UI.
- Counting from screen frames needs temporal logic, not just image classification. The system must know whether a visible card is new.
- Bet advice should include bankroll/risk constraints, not just "bet more when count is high."

## Initial Stack

- Python 3.11+
- FastAPI
- Pydantic
- PyTorch
- NumPy/Pandas
- OpenCV
- Ultralytics YOLO or a lightweight custom classifier for card recognition
- React + Vite
- Tailwind CSS
- WebSockets for live practice state
- SQLite for local MVP, Redis/Postgres later if needed

## First Build Target

The first useful milestone is:

> A local web app where the user plays simulated six-deck blackjack, maintains the count, makes decisions, receives basic-strategy/count-deviation feedback, and sees suggested bet sizing based on true count.

This milestone proves the engine, teaching loop, and product value before investing in RL or screen vision.
