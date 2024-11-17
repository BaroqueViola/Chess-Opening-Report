import requests
import chess
import math

# This function returns {'opening': opening, 'moves': moveList}
def lichess():
    while True:
        gameCode = input('Enter the 8 character game code or the game URL: ')
        if len(gameCode) == 8:
            break
        elif 'lichess.org' in gameCode:
            index = gameCode.find('lichess.org') + 12
            if len(gameCode) >= index + 8: 
                gameCode = gameCode[index:index + 8]
                break
    
    apiUrl = f'https://lichess.org/game/export/{gameCode}?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(apiUrl, headers={'Accept': 'application/json'})

    if response.status_code == 200:
        data = response.json()
    else:
        return 'API error'

    opening = data['opening']['name']
    moveList = data['moves'].split()

    return {'opening': opening, 'moves': moveList}

# This function takes a position and returns the moves data
def qall(fen):
    apiUrl = f'http://www.chessdb.cn/cdb.php?action=queryall&board={fen}&json=true'
    response = requests.get(apiUrl)
    
    if response.status_code == 200:
        data = response.json()
    else:
        return 'API error'
    
    suggestions = {}
    if 'moves' in data:
        for move in data['moves']:
            san = move.get('san')
            centipawn = int(move.get('score'))
            eScore = expectedScore(centipawn,fen)
            suggestions[san] = {'centipawn': centipawn, 'expected score': eScore}
    else:
        return 'No suggestions available.'
    
    return suggestions

# This function takes a position and returns the evaluation
def qscore(fen):
    apiUrl = f'http://www.chessdb.cn/cdb.php?action=queryscore&board={fen}&json=true'
    response = requests.get(apiUrl)

    if response.status_code == 200:
        data = response.json()
    else:
        return 'API error'
    
    if 'eval' in data:
        return expectedScore(data['eval'],fen)
    else:
        return 'No suggestions available.'
    
def winRateParams(fen):
    pos = fen.lower().split()[0]
    # Material count
    m = 9 * pos.count('q') + 5 * pos.count('r') + 3 * pos.count('b') + 3 * pos.count('n') + pos.count('p')
    
    if m > 78:
        m = 78
    elif m < 17:
        m = 17
    
    m /= 58
    
    aList = [-37.45051876, 121.19101539, -132.78783573, 420.70576692]
    bList = [90.26261072, -137.26549898, 71.10130540, 51.35259597]
    
    a = (((aList[0] * m + aList[1]) * m + aList[2]) * m) + aList[3]
    b = (((bList[0] * m + bList[1]) * m + bList[2]) * m) + bList[3]
    
    return a,b

def winRateModel(v,fen):
    a,b = winRateParams(fen)
    return int(0.5 + 1000 / (1 + math.exp((a - v) / b)))

def centipawnTov(centipawn,fen):
    a,b = winRateParams(fen)
    return int(centipawn * a / 100)

# This function takes the centipawn and position, and returns the evaluation
def expectedScore(centipawn,fen):
    v = centipawnTov(centipawn,fen)
    wdlW = winRateModel(v,fen)
    wdlL = winRateModel(-v,fen)
    wdlD = 1000 - wdlW - wdlL
    
    score = (wdlW + wdlD * 0.5) / 1000
    return round(score,4)

# This function takes in a list of moves and returns the analysis
def analysis(moveList, side):
    board = chess.Board()
    fen = board.fen()
    comments = {'analysis': [], 'info': []}

    i = 0
    # i % 2 == 0 when it is white to move, otherwise it is black to move
    while i < min(n, len(moveList)):
        move = moveList[i]
        movesData = qall(fen)

        if side == 'w' and i % 2 == 1:
            board.push_san(move)
            fen = board.fen()
            i += 1
            continue
        elif side == 'b' and i % 2 == 0:
            board.push_san(move)
            fen = board.fen()
            i += 1
            continue

        i += 1

        if movesData != 'No suggestions available.':
            suggestedMoves = list(movesData.keys())
            bestMove = suggestedMoves[0]
            bestEval = movesData[bestMove]['centipawn']
            besteScore = qscore(fen) 
        else:
            comments['info'] = [movesData, i]
            break

        if move in movesData:
            moveEval = movesData[move]['centipawn']
            moveeScore = movesData[move]['expected score']
        else:
            board.push_san(move)
            fen = board.fen()
            continue

        if besteScore - moveeScore > sensitivity:
            comments['analysis'].append({'ply': i, 'move': move, 'best move': bestMove, 'move eval': moveEval\
                , 'best eval': bestEval})

        board.push_san(move)
        fen = board.fen()

    return comments

# Formats the analysis result
def report(comments):
    openingReport = '\nChess opening report\n'
    openingReport += f'\nOpening: {gameData['opening']}\n'
    if len(comments['analysis']) == 0:
        openingReport += '\nNo mistakes found'
        return openingReport
    
    openingReport += '\nImprovements:\n'
    
    for mistake in comments['analysis']:
        moveEval = mistake['move eval']/100
        bestEval = mistake['best eval']/100

        if mistake['ply'] % 2 == 1:
            moveNum = mistake['ply'] // 2 + 1
            openingReport += f'\n{moveNum}. '
            if moveEval > 0:
                moveEval = f'+{moveEval:.2f}'
            else:
                moveEval = f'{moveEval:.2f}'
            if bestEval > 0:
                bestEval = f'+{bestEval:.2f}'
            else:
                bestEval = f'{bestEval:.2f}'

        else:
            moveNum = mistake['ply'] // 2
            openingReport += f'\n{moveNum}... '
            if moveEval > 0:
                moveEval = f'-{moveEval:.2f}'
            elif moveEval < 0:
                moveEval = f'+{-moveEval:.2f}'
            else:
                moveEval = f'{moveEval:.2f}'
            if bestEval > 0:
                bestEval = f'-{bestEval:.2f}'
            elif bestEval < 0:
                bestEval = f'+{-bestEval:.2f}'
            else:
                bestEval = f'{bestEval:.2f}'
        openingReport += f'{mistake['move']} -> {mistake['best move']} ({moveEval} -> {bestEval})'
    
    if len(comments['info']) != 0:
        moveNum = comments["info"][1] // 2
        openingReport += f'\n\nThe analysis was halted early on move {moveNum} \
due to an unexplored position.'

    return openingReport

def getSide():
    while True:
        side = input("Input the side that you want to analyze: ")
        # 'w' for white,'b' for black', 'wb' for both
        if side.lower() in ['w','b','wb']:
            return side

def getSens():
    while True:
        sensitivity = input('Enter the sensitivity: ')
        # 'p' for perfect, 's' for strict, 'n' for normal, 'l' for lenient
        if sensitivity in ['p','s','n','l']:
            sensitivity = {'p': 0.00, 's': 0.02, 'n': 0.05, 'l': 0.10}[sensitivity]
            return sensitivity

def getn():
    while True:
        n = input('Enter the number of moves to analyze: ')
        if n.isnumeric():
            n = int(n)
            n *= 2
            return n

def main():
    global gameData, n, side, sensitivity
    gameData = lichess()
    side = getSide()
    sensitivity = getSens()
    n = getn()

    moveList = gameData['moves']
    print(report(analysis(moveList, side)))
    return 0

main()
