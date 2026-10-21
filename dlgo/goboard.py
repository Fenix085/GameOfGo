import copy
from dlgo.gotypes import Player
from dlgo import zobrist

# tag::strings[]
class GoString():  # <1>
    def __init__(self, colour, stones, liberties):
        self.colour = colour
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return GoString(self.colour, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return GoString(self.colour, self.stones, new_liberties)

    def merged_with(self, go_string):  # <2>
        assert go_string.colour == self.colour
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.colour,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.colour == other.colour and \
            self.stones == other.stones and \
            self.liberties == other.liberties
# <1> Go strings are stones that are linked by a chain of connected stones of the same colour.
# <2> Return a new Go string containing all stones in both strings.
# end::strings[]


# tag::init_zobrist[]
class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD
# end::init_zobrist[]

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        if self._grid.get(point) is not None:
            print('Illegal play on %s' % str(point))
        assert self._grid.get(point) is None
        # 0. Examine the adjacent points.
        adjacent_same_colour = []
        adjacent_opposite_colour = []
        liberties = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.colour == player:
                if neighbor_string not in adjacent_same_colour:
                    adjacent_same_colour.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_colour:
                    adjacent_opposite_colour.append(neighbor_string)
        new_string = GoString(player, [point], liberties)
# tag::apply_zobrist[]
        new_string = GoString(player, [point], liberties)  # <1>

        for same_colour_string in adjacent_same_colour:  # <2>
            new_string = new_string.merged_with(same_colour_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        self._hash ^= zobrist.HASH_CODE[point, player]  # <3>

        for other_colour_string in adjacent_opposite_colour:
            replacement = other_colour_string.without_liberty(point)  # <4>
            if replacement.num_liberties:
                self._replace_string(other_colour_string.without_liberty(point))
            else:
                self._remove_string(other_colour_string)  # <5>
# <1> Until this line `place_stone` remains the same.
# <2> You merge any adjacent strings of the same colour.
# <3> Next, you apply the hash code for this point and player
# <4> Then you reduce liberties of any adjacent strings of the opposite colour.
# <5> If any opposite colour strings now have zero liberties, remove them.
# end::apply_zobrist[]

# tag::unapply_zobrist[]
    def _replace_string(self, new_string): #<1>
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():  # <2>
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None

            self._hash ^= zobrist.HASH_CODE[point, string.colour] #[3]
# <1> This new helper method updates our Go board grid.
# <2> Removing a string can create liberties for other strings.
# <3> With Zobrist hashing, you need to unapply the hash for this move.
# end::unapply_zobrist[]

# tag::board_utils[]
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):  # <1>
        string = self._grid.get(point)
        if string is None:
            return None
        return string.colour

    def get_go_string(self, point):  # <2>
        string = self._grid.get(point)
        if string is None:
            return None
        return string
# <1> Returns the content of a point on the board:  a Player if there is a stone on that point or else None.
# <2> Returns the entire string of stones at a point: a GoString if there is a stone on that point or else None.
# end::board_utils[]

    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
            self.num_cols == other.num_cols and \
            self._grid == other._grid

    def zobrist_hash(self):
        return self._hash

# tag::moves[]
class Move():  # <1>
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):  # <2>
        return Move(point=point)

    @classmethod
    def pass_turn(cls):  # <3>
        return Move(is_pass=True)

    @classmethod
    def resign(cls):  # <4>
        return Move(is_resign=True)
# <1> Any action a player can play on a turn, either is_play, is_pass or is_resign will be set.
# <2> This move places a stone on the board.
# <3> This move passes.
# <4> This move resigns the current game
# end::moves[]

class GameState():
    def __init__(self, board, next_player, previous, move) -> None:
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())}
            )
        self.last_move = move
    
    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)
    
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)
    
    def is_over(self) -> bool:
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass
    
    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0
    
    @property
    def situation(self):
        return (self.next_player, self.board)
    
    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move)
        )