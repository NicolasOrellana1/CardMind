# CardMind

CardMind is a blackjack card-counting and decision-training project.

Phase 1 includes:

- A configurable blackjack rules engine.
- Six-deck shoe simulation with Hi-Lo running count and true count.
- Legal actions for hit, stand, double, split, surrender, and insurance.
- A transparent strategy advisor using basic strategy plus selected count deviations.
- A CLI simulator.
- A polished static trainer UI prototype.
- Unit tests for the engine.

## Run The CLI

```powershell
python -m cardmind.cli --hands 10
```

For interactive play:

```powershell
python -m cardmind.cli --interactive
```

## Run Tests

```powershell
python -m unittest discover -s tests
```

## Open The UI

Open:

```text
C:\blackjackAi\web\index.html
```

The browser UI is a local static prototype for Phase 1. The next phase will connect it to the Python engine through a FastAPI service.

