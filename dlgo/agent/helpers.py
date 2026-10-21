from dlgo.gotypes import Point

def is_point_an_eye(board, point, colour):
    if board.get(point) is not None: # An eye is an empty point
        return False
    for neighbor in point.neighbors(): # All adjacent points must conatin friendly stones
        if board.is_on_grid(neighbor):
            neighbor_colour = board.get(neighbor)
            if neighbor_colour != colour:
                return False
            
    friendly_corners = 0 # we must 3out of 4 corners if the pointis in the middleof the board; on the edge - all corners
    off_board_corners = 0
    corners = [
        Point(point.row - 1, point.col - 1),
        Point(point.row - 1, point.col + 1),
        Point(point.row + 1, point.col - 1),
        Point(point.row + 1, point.col + 1),
    ]
    for corner in corners:
        if board.is_on_grid(corner):
            corner_colour = board.get(corner)
            if corner_colour == colour:
                friendly_corners += 1
        else:
            off_board_corners += 1
    if off_board_corners > 0:
        return off_board_corners + friendly_corners == 4 # point is on the edge
    return friendly_corners >= 3 # point is in the middle