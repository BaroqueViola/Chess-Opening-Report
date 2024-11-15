## Task 1: lichess() (to fix)
Define a function lichess() where the user inputs the 8 character game code e.g. qzsgQdLe, return a dictionary (or JSON if you prefer) containing the following: `{'opening': 'name', 'moves': [list_of_moves]}`

Later we will modify the code so that it accepts game links also.

Example:
```python
lichess()
# User inputs qzsgQdLe
# Returns
{
  'opening': 'Ruy Lopez: Closed, Breyer Defense, Zaitsev Hybrid',
  'moves': ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', 'Ba4', 'Nf6', 'O-O', ...]
}
```
```python
import requests

def lichess():
    
    while True:
        game_code = input("Enter the 8 character game code: ")
        if len(game_code) == 8:
            break
        elif 'lichess.org' in game_code:
            index = game_code.find('lichess.org') + 12
            if len(game_code) >= index + 8: 
                game_code = game_code[index:index + 8]
                break
    
    api_url = 'https://lichess.org/game/export/' + game_code + '?action&tags=false&clocks=false&evals=false&division=false'
    response = requests.get(api_url, headers={"Accept": "application/json"})

    # If API request is successful
    if response.status_code == 200:
        data = response.json()
    else:
        print('API error')
        return 0

    # Get opening name
    opening = data['opening']['name']

    move_list = data['moves'].split()
    return {'opening': opening, 'moves': move_list}
```
## Task 2: get_positions(game)
Define a function get_positions(game) that returns a list containing the position code a.k.a. FEN of each position, including the starting position.

Example:
```python
game = ['e4', 'e5', 'Nf3', 'Nc6']
get_positions(game)
# Returns
['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1',
'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2',
'rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2',
'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3']
```
## Task 3: qall(FEN)
Define a function qall(FEN) that returns a dictionaries which contains the move: evaluation (centipawn), and evaluation (expected score)
Where `expected_score = round(float(move.get('winrate'))*0.01,4)`

Example:
```python
FEN = 'r1bqkb1r/1ppp1ppp/p1n5/4p3/B2Pn3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 6'
qall(FEN)
# Returns
{
  'b5': [-1, 0.4992],
  'Be7': [-5, 0.4962],
  'Bb4': [-102, 0.4233],
  ...
}
```

## Task 4: qscore(FEN)

## Task 5: qbest(FEN)

## Task 6: compare(move)
Define a function compare(move) which compares the evaluation of the move played in the position to the top move in the position. If the difference in expected_score >= sensitivity (let sensitivity = 0.05 for now), return the best move. Else, return the current move.
