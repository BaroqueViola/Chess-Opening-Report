import requests
import chess
import math

# This function returns {'opening': opening, 'moves': moveList}
def lichess():
    # Input validation
    while True:
        gameCode = input('Enter the 8 character game code or the game URL: ')
        if len(gameCode) == 8:
            break
        elif 'lichess.org' in gameCode:
            index = gameCode.find('lichess.org') + 12
            if len(gameCode) >= index + 8: 
                gameCode = gameCode[index:index + 8]
                break
    
    # Getting the PGN (Portable Game Notation) from Lichess
    apiUrl = f'https://lichess.org/game/export/{gameCode}?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(apiUrl, headers={'Accept': 'application/json'})

    if response.status_code == 200:
        data = response.json()
    else:
        return 'API error'

    # Extracting opening name and the list of moves from the data
    opening = data['opening']['name']
    moveList = data['moves'].split()

    return {'opening': opening, 'moves': moveList}

# This function takes a position and returns the suggested moves and corresponding evaluations.
def qall(fen):
    # Using queryall to get information about the position, fen, from ChessDB
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
            # The difference between centipawn and expected score is explored in the documentation.
            suggestions[san] = {'centipawn': centipawn, 'expected score': eScore}
    else:
        return 'No suggestions available.'
    
    return suggestions

# This function takes a position and returns the evaluation
def qscore(fen):
    # Using queryscore to get the evaluation of the position, fen, from ChessDB
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

# The next four functions make up the evaluation conversion model used by Stockfish 17 chess engine.    
def winRateParams(fen):
    # Extracting only the position of the pieces from the fen
    pos = fen.lower().split()[0]
    # Material count is the sum of each piece's values
    m = 9 * pos.count('q') + 5 * pos.count('r') + 3 * pos.count('b') + 3 * pos.count('n') + pos.count('p')
    
    # Bounding m to be between 17 and 78
    if m > 78:
        m = 78
    elif m < 17:
        m = 17
    
    m /= 58
    
    aList = [-37.45051876, 121.19101539, -132.78783573, 420.70576692]
    bList = [90.26261072, -137.26549898, 71.10130540, 51.35259597]
    
    # a and b are win rate parameters based on third degree polynomials of m.
    a = (((aList[0] * m + aList[1]) * m + aList[2]) * m) + aList[3]
    b = (((bList[0] * m + bList[1]) * m + bList[2]) * m) + bList[3]
    
    return a,b

# The win rate model determines how many games out of 1000 the interested player is likely to win.
def winRateModel(v,fen):
    a,b = winRateParams(fen)
    return int(0.5 + 1000 / (1 + math.exp((a - v) / b)))

# This function converts centipawn evaluation to static evaluation.
def centipawnTov(centipawn,fen):
    a,b = winRateParams(fen)
    return int(centipawn * a / 100)

# This function takes the centipawn and position, and returns the expected score
def expectedScore(centipawn,fen):
    v = centipawnTov(centipawn,fen)
    wdlW = winRateModel(v,fen)
    # Loss rate is assumed to be equal and opposite to win rate i.e. flipping every piece's color
    # should return the same values, but for the opposite color.
    wdlL = winRateModel(-v,fen)
    wdlD = 1000 - wdlW - wdlL
    
    # The expected score (float score) ranges from 0 to 1. We can multiply 100% to
    # obtain net win rate (win rate + 0.5 * draw rate) e.g. 0.5 -> 50%
    score = (wdlW + wdlD * 0.5) / 1000
    return round(score,4)

# This function takes in a list of moves and returns the analysis
def analysis(moveList, side):
    # This program assumes and initializes the default starting position.
    board = chess.Board()
    # Obtain the fen (board notation)
    fen = board.fen()
    comments = {'analysis': [], 'info': []}

    i = 0
    # i % 2 == 0 when it is white to move, otherwise it is black to move
    while i < min(n, len(moveList)):
        move = moveList[i]
        movesData = qall(fen)

        # Increments and skips when it is not the color we would like to analyze.
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
            # When we reach an unanalyzed position, we halt the analysis and record the ply at which we stopped.
            comments['info'] = [movesData, i]
            break

        if move in movesData:
            moveEval = movesData[move]['centipawn']
            moveeScore = movesData[move]['expected score']
        else:
            # If the move played is not found on the database, we assume it is a bad move.
            board.push_san(move)
            fen = board.fen()
            comments['analysis'].append({'ply': i, 'move': move, 'best move': bestMove, 'move eval': '??'\
                , 'best eval': bestEval})
            continue
        
        evalDiff = besteScore - moveeScore
        if evalDiff > sensitivity:
            # Notates the move played with '??' (blunder), '?' (mistake), or '?!' (inaccuracy) based on the difference in evaluation
            if evalDiff > 0.20:
                moveAnnotated = move + '??'
            elif evalDiff > 0.10:
                moveAnnotated = move + '?'
            elif evalDiff > 0.05:
                moveAnnotated = move + '?!'
            else:
                moveAnnotated = move

            comments['analysis'].append({'ply': i, 'move': moveAnnotated, 'best move': bestMove, 'move eval': moveEval\
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
        if mistake['move eval'] != '??':
            # Converting centipawn to pawn
            moveEval = mistake['move eval']/100
            bestEval = mistake['best eval']/100

            if mistake['ply'] % 2 == 1:
                # If it is white's move, notate it as number. e.g. 1.
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
                # If it is black's move, notate it as number.. e.g. 1...
                moveNum = mistake['ply'] // 2
                openingReport += f'\n{moveNum}... '

                # Converting evaluation from black's perspective to white's perspective for consistency
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
        # 'w' for white, 'b' for black', 'wb' for both
        if side.lower() in ['w','b','wb']:
            return side

def getSens():
    while True:
        sensitivity = input('Enter the sensitivity: ')
        # 'p' for perfect, 's' for strict, 'n' for normal, 'l' for lenient
        if sensitivity in ['p','s','n','l']:
            # Change in net win rate of 0%, 2%, 5%, and 10%
            sensitivity = {'p': 0.00, 's': 0.02, 'n': 0.05, 'l': 0.10}[sensitivity]
            return sensitivity

def getn():
    while True:
        n = input('Enter the number of moves to analyze: ')
        if n.isnumeric():
            n = int(n)
            # Doubled because each side makes one action (ply) = 2 plys per move
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