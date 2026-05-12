from __future__ import annotations

from dataclasses import dataclass

from .engine import BlackjackGame, GameConfig
from .strategy import StrategyAdvisor


@dataclass(frozen=True)
class SimulationSummary:
    hands: int
    total_net: float
    average_net: float
    win_rate: float
    loss_rate: float
    push_rate: float
    final_running_count: int
    final_true_count: float


def run_simulation(hands: int, seed: int | None = None, config: GameConfig | None = None) -> SimulationSummary:
    game = BlackjackGame(config or GameConfig(), seed=seed)
    advisor = StrategyAdvisor()
    wins = losses = pushes = 0
    total = 0.0

    for _ in range(hands):
        bet = advisor.bet_units(game.shoe.true_count)
        result = game.play_round(advisor.policy, bet=bet)
        total += result.net
        if result.net > 0:
            wins += 1
        elif result.net < 0:
            losses += 1
        else:
            pushes += 1

    return SimulationSummary(
        hands=hands,
        total_net=total,
        average_net=total / hands if hands else 0.0,
        win_rate=wins / hands if hands else 0.0,
        loss_rate=losses / hands if hands else 0.0,
        push_rate=pushes / hands if hands else 0.0,
        final_running_count=game.shoe.running_count,
        final_true_count=game.shoe.true_count,
    )

