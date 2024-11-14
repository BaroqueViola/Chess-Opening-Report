import math

def evalconversion(centipawn):
    
def win_rate(x):
    return 1 / (1 + math.exp(-(x-a)/b))
def loss_rate(x):
    return win_rate(-x)
def draw_rate(x):
    return 1 - win_rate(x) - loss_rate(x)
print(evalconversion(5))
