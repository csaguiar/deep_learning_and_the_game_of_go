import copy

from dlgo.hexpawn._types import Player, Point

__all__ = [
    'Board',
    'GameState',
    'Move',
]

BOARD_SIZE = 3
ROWS = tuple(range(1, BOARD_SIZE + 1))
COLS = tuple(range(1, BOARD_SIZE + 1))
# Top left to lower right diagonal
DIAG_1 = (Point(1, 1), Point(2, 2), Point(3, 3))
# Top right to lower left diagonal
DIAG_2 = (Point(1, 3), Point(2, 2), Point(3, 1))


class Board:
    def __init__(self):
        self._grid = {}
        self._end_board = {}
        # End board
        self._end_board[Player.o] = max(ROWS)
        self._end_board[Player.x] = min(ROWS)

        # Position pawns:
        for i in range(1, 4):
            self._grid[Point(1, i)] = Player.o
            self._grid[Point(3, i)] = Player.x

    def place(self, player, point_start, point_end):
        assert self.is_on_grid(point_end)
        self._grid[point_start] = None
        self._grid[point_end] = player

    @staticmethod
    def is_on_grid(point):
        return 1 <= point.row <= BOARD_SIZE and \
            1 <= point.col <= BOARD_SIZE

    def get(self, point):
        """Return the content of a point on the board.

        Returns None if the point is empty, or a Player if there is a
        stone on that point.
        """
        return self._grid.get(point)


class Move:
    def __init__(self, point_start, point_end):
        self.point_start = point_start
        self.point_end = point_end


class GameState:
    def __init__(self, board, next_player, move):
        self.board = board
        self.next_player = next_player
        self.last_move = move

    def apply_move(self, move):
        """Return the new GameState after applying the move."""
        next_board = copy.deepcopy(self.board)
        next_board.place(self.next_player, move.point_start, move.point_end)
        return GameState(next_board, self.next_player.other, move)

    @classmethod
    def new_game(cls):
        board = Board()
        return GameState(board, Player.x, None)

    def find_moves(self, player):
        moves = []
        dir_forward = 1 if player == Player.o else -1
        for point, this_player in self.board._grid.items():
            if this_player is player:
                for i in range(3):
                    end_point = Point(point.row+dir_forward, point.col+i-1)
                    move = Move(point, end_point)
                    if self.is_valid_move(move, player):
                        moves.append(move)
        return moves

    def is_valid_move(self, move, player):
        is_out_of_board = (
            move.point_end.row > max(ROWS) or
            move.point_end.row < min(ROWS) or
            move.point_end.col > max(COLS) or
            move.point_end.col < min(COLS)
        )

        is_diag = (
            abs(move.point_end.col - move.point_start.col) == 1 and
            abs(move.point_end.row - move.point_start.row) == 1
        )

        is_kill = is_diag and self.board.get(move.point_end) is player.other

        is_forward = (move.point_end.col == move.point_start.col) and self.board.get(move.point_end) is None

        return (is_forward or is_kill) and not is_out_of_board

    def legal_moves(self):
        return self.find_moves(self.next_player)

    def is_over(self):
        # Reach end
        o_pawns = 0
        x_pawns = 0
        for point, player in self.board._grid.items():
            if player is not None:
                end_board = self.board._end_board[player]
                reached_end = point.row == end_board
                break

        # No moves
        n_moves = self.find_moves(self.next_player)
        o_moves = self.find_moves(self.next_player.other)
        no_moves = len(n_moves) == 0 or len(o_moves) == 0

        # No pawns
        o_pawns = 0
        x_pawns = 0
        for point, player in self.board._grid.items():
            if player == Player.x:
                x_pawns += 1
            if player == Player.o:
                o_pawns += 1
        no_pawns = o_pawns == 0 or x_pawns == 0

        return reached_end or no_pawns or no_moves

    def _has_3_in_a_row(self, player):
        # Vertical
        for col in COLS:
            if all(self.board.get(Point(row, col)) == player for row in ROWS):
                return True
        # Horizontal
        for row in ROWS:
            if all(self.board.get(Point(row, col)) == player for col in COLS):
                return True
        # Diagonal UL to LR
        if self.board.get(Point(1, 1)) == player and \
                self.board.get(Point(2, 2)) == player and \
                self.board.get(Point(3, 3)) == player:
            return True
        # Diagonal UR to LL
        if self.board.get(Point(1, 3)) == player and \
                self.board.get(Point(2, 2)) == player and \
                self.board.get(Point(3, 1)) == player:
            return True
        return False

    def is_end(self, player):
        end_row = self.board._end_board[player]
        is_pawn_end = False
        for col in range(1, 4):
            if self.board._grid[end_row, col] is player:
                is_pawn_end = True

        return is_pawn_end

    def winner(self):
        if self.is_end(Player.x):
            return Player.x

        if self.is_end(Player.o):
            return Player.o

        if self.find_moves(Player.o):
            return Player.x

        if self.find_moves(Player.x):
            return Player.o

        return None
