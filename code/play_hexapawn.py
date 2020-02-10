from dlgo import minimax
from dlgo import hexpawn

from six.moves import input

COL_NAMES = 'ABC'


def print_board(board):
    print('   A   B   C')
    for row in (1, 2, 3):
        pieces = []
        for col in (1, 2, 3):
            piece = board.get(hexpawn.Point(row, col))
            if piece == hexpawn.Player.x:
                pieces.append('X')
            elif piece == hexpawn.Player.o:
                pieces.append('O')
            else:
                pieces.append(' ')
        print('%d  %s' % (row, ' | '.join(pieces)))


def point_from_coords(text):
    col_name = text[0]
    row = int(text[1])
    return hexpawn.Point(row, COL_NAMES.index(col_name) + 1)


def main():
    game = hexpawn.GameState.new_game()

    human_player = hexpawn.Player.x
    # bot_player = hexpawn.Player.o

    bot = minimax.MinimaxAgent()

    while not game.is_over():
        print_board(game.board)
        if game.next_player == human_player:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = hexpawn.Move(point)
        else:
            move = bot.select_move(game)
        game = game.apply_move(move)

    print_board(game.board)
    winner = game.winner()
    if winner is None:
        print("It's a draw.")
    else:
        print('Winner: ' + str(winner))


if __name__ == '__main__':
    main()
