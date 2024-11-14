# Code structure

```python
gameData = lichess()
# User inputs 8 character game code or a lichess link

side = input()
# User inputs the color to analyze, either white, black, or both.

sensitivity = float(input('Enter the sensitivity: '))
# User inputs the desired analysis sensitivity, or leave empty for default value

n = 2 * int(input('Enter the number of moves to analyze: '))
# User inputs the number of moves to analyze. Note that since a move includes both white's and black's, we times 2.

main()
# Runs through necessary codes to give the opening report.
# This includes going through the moves, getting the FEN for each, get the evaluation of the position of the move played and of the best move. Add the improved move and the corresponding evals to a list Print the opening report, including the opening name.
```
