import requests
#requests package can be used to get API

#Grabs PGN (game notation) from lichess API
#api_url = 'https://lichess.org/game/export/[game ID]?action=pgnInJson'
#Add ?action=[action]... to specify request, & to include multiple requests
api_url = 'https://lichess.org/game/export/28BX1zzd?action=pgnInJson&tags=false&clocks=false&evals=false'
response = requests.get(api_url)

# If the responses status code is 200 (success)
if response.status_code == 200:
    #data = response.json()
    print(response.text)
    #prints the game notation

#Grabs evaluation of a given FEN (position) from chessdb API

#api_url = 'http://www.chessdb.cn/cdb.php?action=[ACTION]{&[OPTION1]=[VALUE1]...&[OPTIONn]=[VALUEn]}'
#api_url = 'http://www.chessdb.cn/cdb.php?action=queryall{&board=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1}'
