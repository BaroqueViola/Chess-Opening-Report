import requests
import chess
import math

def lichess():
    
    while True:
        game_code = input('Enter the 8 character game code or the game URL: ')
        if len(game_code) == 8:
            break
        elif 'lichess.org' in game_code:
            index = game_code.find('lichess.org') + 12
            if len(game_code) >= index + 8: 
                game_code = game_code[index:index + 8]
                break
    
    api_url = f'https://lichess.org/game/export/{game_code}?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(api_url, headers={'Accept': 'application/json'})

    # If API request is successful
    if response.status_code == 200:
        data = response.json()
    else:
        return 'API error'

    opening = data['opening']['name']

    move_list = data['moves'].split()
    return {'opening': opening, 'moves': move_list}

def get_positions(moves):
    board = chess.Board()
    fens = []
    fens.append(board.fen())
    for move in moves:
        board.push_san(move)
        fens.append(board.fen())
    return fens

def qall(fen):
    # Fetches suggested moves from ChessDB for a given FEN and formats them as a dictionary.
    api_url = f'http://www.chessdb.cn/cdb.php?action=queryall&board={fen}&json=true'
    response = requests.get(api_url)
    
    suggestions = {}
    if response.status_code == 200:
        data = response.json()
        if 'moves' in data:
            for move in data['moves']:
                san = move.get('san')
                centipawn = int(move.get('score'))
                expected_score = round(float(move.get('winrate')) * 0.01, 4)
                suggestions[san] = [centipawn, expected_score]
        else:
            return 'No suggestions available.'
    else:
        return 'API error'
    return suggestions

def qscore(fen):
    # Fetches the evaluation from ChessDB for a given FEN.
    api_url = f'http://www.chessdb.cn/cdb.php?action=queryscore&board={fen}&json=true'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if 'eval' in data:
            centipawn = data['eval']
        else:
            return 'No suggestions available.'
    else:
        return 'API error'
    return expectedScore(centipawn,fen)

def qbest(fen):
    api_url = f'http://www.chessdb.cn/cdb.php?action=querybest&board={fen}&json=true'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if 'move' in data:
            move_uci = data['move']
            board = chess.Board()
            board.set_fen(fen)
            move_obj = chess.Move.from_uci(move_uci)
            move_san = board.san(move_obj)
        else:
            return 'No suggestions available.'
    else:
        return 'API error'
    return move_san

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

def analysis(fens):
    return 0

def main():
    gameData = lichess()
    positions = get_positions(gameData['moves'])
    analysis(positions)
    return 0

print(qbest('r1bqkb1r/1ppp1ppp/p1n5/4p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 6'))