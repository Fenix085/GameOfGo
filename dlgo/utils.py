#tag::print_utils[]
from typing import Dict, Optional

from dlgo import gotypes

COLS = 'ABCDEFGHJKLMNOPQRST'
STONE_TO_CHAR = {
    None: ' . ',
    gotypes.Player.black: ' x ',
    gotypes.Player.white: ' o ',
}

def print_move(player, move):
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
    print('%s %s' % (player, move_str))

def print_board(board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(gotypes.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))

def point_from_coords(coords):
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])
    return gotypes.Point(row=row, col=col)

def coords_from_point(point):
    return '%s%d' % (
        COLS[point.col - 1],
        point.row
    )
# end::print_utils[]

class MoveAge:
    def __init__(self, board):
        self.ages: Dict[gotypes.Point, Optional[int]] = {
            gotypes.Point(row=row, col=col): None
            for row in range(1, board.num_rows + 1)
            for col in range(1, board.num_cols + 1)
        }

    def increment_all(self):
        for point, age in self.ages.items():
            if age is not None:
                self.ages[point] = age + 1

    def add(self, point):
        self.ages[point] = 0

    def reset_age(self, point):
        self.ages[point] = None
