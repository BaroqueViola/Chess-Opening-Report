## Lichess formula
```python
import math

def score(centipawn):
    return round((50 + 50 * (2 / (1 + math.exp(-0.00368208 * centipawn)) - 1)) / 100, 4)
```
## Stockfish formula (use this)
```python
import math
import chess

"""
m is material count
a and b are conversion parameters
v is static evaluation
"""

def centipawnTov(centipawn,fen):
    a,b = winRateParams(fen)
    return int(centipawn * a / 100)
    
def winRateParams(fen):
    fen2 = fen.lower().split()[0]
    # Material count
    m = 9 * fen2.count('q') + 5 * fen2.count('r') + 3 * fen2.count('b') + 3 * fen2.count('n') + fen2.count('p')
    
    if m > 78:
        m = 78
    elif m < 17:
        m = 17
    
    m /= 58
    
    a_s = [-37.45051876, 121.19101539, -132.78783573, 420.70576692]
    b_s = [90.26261072, -137.26549898, 71.10130540, 51.35259597]
    
    a = (((a_s[0] * m + a_s[1]) * m + a_s[2]) * m) + a_s[3]
    b = (((b_s[0] * m + b_s[1]) * m + b_s[2]) * m) + b_s[3]
    
    return a,b

def winRateModel(v,fen):
    a,b = winRateParams(fen)
    return int(0.5 + 1000 / (1 + math.exp((a - v) / b)))

def expectedScore(centipawn,fen):
    v = centipawnTov(centipawn,fen)
    wdl_w = winRateModel(v,fen)
    wdl_l = winRateModel(-v,fen)
    wdl_d = 1000 - wdl_w - wdl_l
    
    score = (wdl_w + wdl_d * 0.5)/1000
    return round(score,4)
 
print(expectedScore(177,'rnbqkbnr/ppppp1pp/8/5p2/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2'))
```