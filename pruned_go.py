from six.moves import input

from dlgo import goboard_fast
from dlgo import gotypes
from dlgo import minimax
from dlgo.utils import print_board, print_move, point_from_coords

BORAD_SIZE = 5

def capture_diff(game_state):
    black_stones = 0
    white_stones = 0
    for r in range(1, game_state.board.num_rows + 1):
        for c in range(1, game_state.board.num_cols + 1):
            p = gotypes.Point(r, c)
            colour = game_state.board.get(p)
            if colour == gotypes.Player.black:
                black_stones += 1
            elif colour == gotypes.Player.white:
                white_stones += 1
    diff = black_stones - white_stones
    if game_state.next_player == gotypes.Player.black:
        return diff
    return -1 * diff

def main():
    game = goboard_fast.GameState.new_game(BORAD_SIZE)
    bot = minimax.DepthPruneAgent(3, capture_diff)

    while not game.is_over():
        print_board(game.board)
        if game.next_player == gotypes.Player.black:
            human_move = input("-- ")
            point = point_from_coords(human_move.strip())
            move = goboard_fast.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)

if __name__ == "__main__":
    main()