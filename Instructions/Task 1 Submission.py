import requests
import chess

def lichess():
    
    game_code = input("Enter the 8 character game code: ")
    api_url = 'https://lichess.org/game/export/' + game_code + '?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(api_url, headers={"Accept": "application/json"})

    # If API request is successful
    if response.status_code == 200:
        data = response.json()
    else:
        print('API error')
        return 0

    # Prints opening name
    print('Opening:', data['opening']['name'])

    move_list = data['moves'].split()
    return move_list

def qall(fen):
    """
    Fetches suggested moves from ChessDB for a given FEN and formats them as a dictionary.
    """
    api_url = f'http://www.chessdb.cn/cdb.php?action=queryall&board={fen}&json=true'
    response = requests.get(api_url)
    
    suggestions = {}
    if response.status_code == 200:
        data = response.json()
        if 'moves' in data:
            for move in data['moves']:
                san = move.get('san')
                score = int(move.get('score'))
                expected_score = round(float(move.get('winrate')) * 0.01, 4)
                suggestions[san] = [score, expected_score]
        else:
            print("No suggestions available.")
    else:
        print("API error")
    return suggestions

def get_positions(moves):
    """
    Plays each move on a chess board and returns a list of FEN strings for each position.
    """
    board = chess.Board()
    fens = []
    for move in moves:
        board.push_san(move)
        fens.append(board.fen())
    return fens

def display(fens):
    """
    Takes a list of FENs and prints suggested moves for each position.
    """
    for index, fen in enumerate(fens):
        print(f"\nPosition {index + 1} FEN: {fen}")
        suggestions = qall(fen)
        print("Suggestions:", suggestions)
        
        
display(get_positions(lichess()))
