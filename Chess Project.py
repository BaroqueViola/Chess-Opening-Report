import requests

def lichess():
    # User inputs the game code (to do: implement input game link)
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

    # Prints a list of each move, good for future iteration
    move_list = data['moves'].split()
    print(move_list)

def qall(FEN):
    api_url = 'http://www.chessdb.cn/cdb.php?action=queryall&board=' + FEN + '&json=true'
    response = requests.get(api_url)
    
    # If API request is successful
    if response.status_code == 200:
        data = response.json()
    else:
        print('API error')
        return 0
    
    # Prints the ordered suggested moves and evaluation
    if 'moves' in data:
            moves = data['moves']
            print('Suggested Moves and Evaluations:')
            for move in moves:
                print(f"Move: {move.get('san')}, {move.get('score')}, \
{round(float(move.get('winrate'))*0.01,4)}")

def qbest(FEN):
    api_url = 'http://www.chessdb.cn/cdb.php?action=querybest&board=' + FEN + '&json=true'
    response = requests.get(api_url)
    
    # If API request is successful
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('API error')
        return 0

def qscore(FEN):
    api_url = 'http://www.chessdb.cn/cdb.php?action=queryscore&board=' + FEN + '&json=true'
    response = requests.get(api_url)
    
    # If API request is successful
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('API error')
        return 0
                
#lichess()
#qall('r1bqkb1r/1ppp1ppp/p1n5/4p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 6')
qbest('r1bqkb1r/1ppp1ppp/p1n5/4p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 6')
qscore('r1bqkb1r/1ppp1ppp/p1n5/4p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 6')
