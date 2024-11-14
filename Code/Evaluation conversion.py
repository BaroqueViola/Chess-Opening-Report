import math

# Lichess formula
def score(centipawn):
    return round((50 + 50 * (2 / (1 + math.exp(-0.00368208 * centipawn)) - 1)) / 100, 4)

# Stockfish formula (WIP)
def win_rate(x):
    return 1 / (1 + math.exp(-(x-a)/b))
def loss_rate(x):
    return win_rate(-x)
def draw_rate(x):
    return 1 - win_rate(x) - loss_rate(x)
print(evalconversion(5))
