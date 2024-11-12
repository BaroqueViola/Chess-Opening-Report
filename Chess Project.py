import requests

def lichess():
    game_code = input("Enter the game code: ")
    api_url = 'https://lichess.org/game/export/' + game_code + '?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(api_url, headers={"Accept": "application/json"})

    if response.status_code == 200:
        data = response.json()
        #print(data)

    # Prints opening name
    print(data['opening']['name'])

    # Prints a list of each move, good for future iteration
    move_list = data['moves'].split()
    print(move_list)

def chessdb(FEN):
    api_url = 'http://www.chessdb.cn/cdb.php?action=queryall&board=' + FEN + '&json=true'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
    else:
        print('API error')

    if 'moves' in data:
            moves = data['moves']
            print('Suggested Moves and Evaluations:')
            for move in moves:
                print(f"Move: {move.get('san')}, Centipawn evaluation: {move.get('score')},\
Expected score: {round(float(move.get('winrate'))*0.01,4)}")
                
lichess()
chessdb('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
