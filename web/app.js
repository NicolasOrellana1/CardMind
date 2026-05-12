const ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const suits = ["clubs", "diamonds", "hearts", "spades"];
const suitSymbol = { clubs: "♣", diamonds: "♦", hearts: "♥", spades: "♠" };

let shoe = [];
let runningCount = 0;
let bankroll = 100;
let bet = 1;
let player = [];
let dealer = [];
let roundActive = false;
let revealDealer = false;

const el = (id) => document.getElementById(id);

function buildShoe() {
  const cards = [];
  for (let d = 0; d < 6; d += 1) {
    for (const suit of suits) {
      for (const rank of ranks) cards.push({ rank, suit });
    }
  }
  for (let i = cards.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]];
  }
  shoe = cards;
  runningCount = 0;
}

function hiLo(card) {
  if (["2", "3", "4", "5", "6"].includes(card.rank)) return 1;
  if (["10", "J", "Q", "K", "A"].includes(card.rank)) return -1;
  return 0;
}

function draw() {
  if (shoe.length < 20) buildShoe();
  const card = shoe.pop();
  runningCount += hiLo(card);
  return card;
}

function value(card) {
  if (card.rank === "A") return 11;
  if (["J", "Q", "K"].includes(card.rank)) return 10;
  return Number(card.rank);
}

function total(hand) {
  let sum = hand.reduce((acc, card) => acc + value(card), 0);
  let aces = hand.filter((card) => card.rank === "A").length;
  while (sum > 21 && aces > 0) {
    sum -= 10;
    aces -= 1;
  }
  return sum;
}

function isSoft(hand) {
  const hard = hand.reduce((acc, card) => acc + value(card), 0);
  return hand.some((card) => card.rank === "A") && hard <= 21;
}

function trueCount() {
  return runningCount / Math.max(shoe.length / 52, 0.25);
}

function betUnits() {
  const tc = trueCount();
  if (tc < 1) return 1;
  return Math.min(12, 1 + Math.floor(tc * 2));
}

function dealerValue(card) {
  if (!card) return 0;
  return card.rank === "A" ? 11 : Math.min(value(card), 10);
}

function canSplit(hand) {
  return hand.length === 2 && Math.min(value(hand[0]), 10) === Math.min(value(hand[1]), 10);
}

function advice() {
  if (!roundActive) return { action: "Ready", reason: "Deal a hand and keep the running count as cards appear." };
  const up = dealerValue(dealer[0]);
  const handTotal = total(player);
  const soft = isSoft(player);
  const tc = trueCount();

  if (!soft && handTotal === 16 && up === 10 && tc >= 0) return { action: "Stand", reason: "Index play: stand on hard 16 vs 10 at true count 0 or higher." };
  if (!soft && handTotal === 15 && up === 10 && tc >= 4) return { action: "Stand", reason: "Index play: stand on hard 15 vs 10 at true count +4 or higher." };
  if (canSplit(player) && ["A", "8"].includes(player[0].rank)) return { action: "Split", reason: "Basic strategy splits aces and eights." };
  if (canSplit(player) && ["10", "J", "Q", "K"].includes(player[0].rank)) return { action: "Stand", reason: "Basic strategy keeps paired tens together." };
  if (soft && player.length === 2 && handTotal >= 19) return { action: "Stand", reason: "Strong soft total. Keep the made hand." };
  if (handTotal >= 17) return { action: "Stand", reason: "Basic strategy stands on hard 17 or better." };
  if (handTotal >= 13 && handTotal <= 16) return up >= 2 && up <= 6
    ? { action: "Stand", reason: "Dealer is weak. Stand and let the dealer draw." }
    : { action: "Hit", reason: "Dealer is strong. Improve the hand." };
  if (handTotal === 12) return up >= 4 && up <= 6
    ? { action: "Stand", reason: "Stand on 12 only against dealer 4 through 6." }
    : { action: "Hit", reason: "12 is too fragile against this upcard." };
  if (handTotal === 11) return { action: "Double", reason: "Double 11 against most dealer upcards." };
  if (handTotal === 10 && up <= 9) return { action: "Double", reason: "Double 10 against dealer 2 through 9." };
  if (handTotal === 9 && up >= 3 && up <= 6) return { action: "Double", reason: "Double 9 against dealer 3 through 6." };
  return { action: "Hit", reason: "Basic strategy improves low totals." };
}

function cardHtml(card, hidden = false) {
  if (hidden) return `<div class="card back" aria-label="hidden card"></div>`;
  const red = ["diamonds", "hearts"].includes(card.suit) ? " red" : "";
  const mark = suitSymbol[card.suit];
  return `<div class="card${red}"><span>${card.rank}${mark}</span><span class="pip">${mark}</span><span class="corner bottom">${card.rank}${mark}</span></div>`;
}

function render() {
  const dealerShown = revealDealer ? dealer : dealer.slice(0, 1);
  el("dealerCards").innerHTML = dealerShown.map((card) => cardHtml(card)).join("") + (!revealDealer && dealer.length > 1 ? cardHtml(null, true) : "");
  el("playerCards").innerHTML = player.map((card) => cardHtml(card)).join("");
  el("playerTotal").textContent = player.length ? `${total(player)}${isSoft(player) ? " soft" : ""}` : "0";
  el("dealerTotal").textContent = revealDealer && dealer.length ? total(dealer) : dealer.length ? "?" : "0";
  el("runningCount").textContent = String(runningCount);
  el("trueCount").textContent = trueCount().toFixed(1);
  el("betUnits").textContent = `${betUnits()}u`;
  el("bankroll").textContent = `${bankroll.toFixed(1)}u`;
  el("cardsLeft").textContent = String(shoe.length);
  el("summaryPlayer").textContent = player.length ? `${total(player)}${isSoft(player) ? " soft" : ""}` : "-";
  el("summaryDealer").textContent = dealer[0] ? `${dealer[0].rank}${suitSymbol[dealer[0].suit]}` : "-";
  el("shoeStatus").textContent = `${Math.ceil(shoe.length / 52)} decks left`;
  const tip = advice();
  el("adviceAction").textContent = tip.action;
  el("adviceReason").textContent = tip.reason;
  el("dealBtn").disabled = roundActive;
  el("hitBtn").disabled = !roundActive;
  el("standBtn").disabled = !roundActive;
  el("doubleBtn").disabled = !roundActive || player.length !== 2;
}

function deal() {
  revealDealer = false;
  roundActive = true;
  bet = betUnits();
  player = [draw(), draw()];
  dealer = [draw(), draw()];
  el("message").textContent = "Make the best decision, then compare it to the advisor.";
  if (total(player) === 21) stand();
  render();
}

function hit() {
  player.push(draw());
  if (total(player) > 21) {
    bankroll -= bet;
    roundActive = false;
    revealDealer = true;
    el("message").textContent = `Bust. Lost ${bet} unit${bet === 1 ? "" : "s"}.`;
  }
  render();
}

function dealerPlay() {
  revealDealer = true;
  while (total(dealer) < 17) dealer.push(draw());
}

function stand(multiplier = 1) {
  bet *= multiplier;
  dealerPlay();
  const p = total(player);
  const d = total(dealer);
  let net = 0;
  if (p > 21) net = -bet;
  else if (d > 21 || p > d) net = bet;
  else if (p < d) net = -bet;
  bankroll += net;
  roundActive = false;
  el("message").textContent = net > 0 ? `Won ${net} units.` : net < 0 ? `Lost ${Math.abs(net)} units.` : "Push. Bankroll unchanged.";
  render();
}

function reset() {
  buildShoe();
  player = [];
  dealer = [];
  bankroll = 100;
  bet = 1;
  roundActive = false;
  revealDealer = false;
  el("message").textContent = "Fresh shoe. Deal when ready.";
  render();
}

el("dealBtn").addEventListener("click", deal);
el("hitBtn").addEventListener("click", hit);
el("standBtn").addEventListener("click", () => stand());
el("doubleBtn").addEventListener("click", () => {
  player.push(draw());
  stand(2);
});
el("resetBtn").addEventListener("click", reset);

reset();

