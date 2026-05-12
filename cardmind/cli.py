from __future__ import annotations

import argparse

from .actions import Action
from .engine import BlackjackGame
from .hand import Hand
from .simulator import run_simulation
from .strategy import StrategyAdvisor


def format_hand(hand: Hand) -> str:
    soft = " soft" if hand.is_soft else ""
    return f"{' '.join(hand.labels())} ({hand.total}{soft})"


def parse_action(raw: str) -> Action | None:
    lookup = {
        "h": Action.HIT,
        "hit": Action.HIT,
        "s": Action.STAND,
        "stand": Action.STAND,
        "d": Action.DOUBLE,
        "double": Action.DOUBLE,
        "p": Action.SPLIT,
        "split": Action.SPLIT,
        "r": Action.SURRENDER,
        "surrender": Action.SURRENDER,
    }
    return lookup.get(raw.strip().lower())


def interactive() -> None:
    game = BlackjackGame()
    advisor = StrategyAdvisor()
    print("CardMind interactive blackjack. Type q to quit.")
    while True:
        bet = advisor.bet_units(game.shoe.true_count)
        player_hands, dealer = game.start_round(bet=bet)
        hand = player_hands[0]
        print("\nNew hand")
        print(f"Dealer: {dealer.cards[0].label}")
        print(f"You:    {format_hand(hand)}")
        print(f"Count:  RC {game.shoe.running_count}, TC {game.shoe.true_count:.1f}, suggested bet {bet}u")

        while not hand.resolved and not hand.is_bust:
            legal = game.legal_actions(hand, dealer.cards[0])
            advice = advisor.advise(hand, dealer.cards[0], game.shoe.true_count)
            print(f"Advisor: {advice.action.value.upper()} - {advice.reason}")
            print("Actions:", ", ".join(sorted(action.value for action in legal)))
            raw = input("> ")
            if raw.lower().strip() == "q":
                return
            action = parse_action(raw)
            if action not in legal:
                print("That action is not legal here.")
                continue
            if action == Action.HIT:
                hand.add(game.shoe.draw())
            elif action == Action.STAND:
                hand.resolved = True
            elif action == Action.DOUBLE:
                hand.bet *= 2
                hand.add(game.shoe.draw())
                hand.resolved = True
            elif action == Action.SURRENDER:
                hand.is_surrendered = True
                hand.resolved = True
            elif action == Action.SPLIT:
                print("Interactive split play lands in Phase 2 UI; simulator supports it.")
                hand.resolved = True
            print(f"You: {format_hand(hand)}")

        completed = [hand]
        if any(not h.is_bust and not h.is_surrendered for h in completed):
            game.dealer_play(dealer)
        payouts = game.settle(completed, dealer)
        print(f"Dealer: {format_hand(dealer)}")
        print(f"Net: {sum(payouts):+.1f} units")


def main() -> None:
    parser = argparse.ArgumentParser(description="CardMind blackjack simulator")
    parser.add_argument("--hands", type=int, default=1000, help="Number of simulated hands")
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument("--interactive", action="store_true", help="Play an interactive CLI hand loop")
    args = parser.parse_args()

    if args.interactive:
        interactive()
        return

    summary = run_simulation(args.hands, seed=args.seed)
    print(f"Hands:          {summary.hands}")
    print(f"Total net:      {summary.total_net:+.1f} units")
    print(f"Average net:    {summary.average_net:+.4f} units/hand")
    print(f"Win/loss/push:  {summary.win_rate:.1%} / {summary.loss_rate:.1%} / {summary.push_rate:.1%}")
    print(f"Final count:    RC {summary.final_running_count}, TC {summary.final_true_count:.2f}")


if __name__ == "__main__":
    main()

