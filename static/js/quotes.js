document.addEventListener("DOMContentLoaded", function () {
  // list of random "hilarious" quotes
  const quotes = [
    "When does it rain money? When there's change in the air",
    "My wallet is like an onion, opening it makes me cry.",
    "Girls just wanna have funds.",
    "My friends say I'm cheap, but I'm not buying it.",
    "What did the duck say after going shopping? Put it on my bill.",
    "If money doesn't grow on trees, then why do banks have branches?",
    "What do you call a belt made of $100? A waist of money.",
    "Why is money called dough? Because we need it.",
    "Knock, knock. Who's there? I.O... I.O who? Me, when can pay me back?",
    "Where do polar bears keep their money? At a snow bank.",
    "What do you call pasta with no money? Penne-less.",
    "Knock, knock. Who's there? Cash... Cash who? No, thanks, I prefer peanuts",
    "Why are money jokes funny? Because they make cents!",
    "Pigeons are the richest birds. They don't mind making deposits on expensive cars.",
    "I wish my wallet came with free refills!",
    "Why did the robber take a bath before he robbed the bank? To make a clean getaway.",
    "They call me lack toast intolerant the way I can't live without cash.",
  ];

  // display random quote js
  const quoteBox = document.getElementById("quote-line");
  if (quoteBox) {
    quoteBox.textContent = quotes[Math.floor(Math.random() * quotes.length)];
  }
});
