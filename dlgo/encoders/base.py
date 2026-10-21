import importlib

__all__ = [
    'Encoder',
    'get_encoder_by_name',
]

# tag::base_encoder[]
class Encoder:
    def name(self): # lets support logging or saving the name of encoder model is using
        raise NotImplementedError()
    
    def encode(self, game_state): # turn board into numeric data
        raise NotImplementedError()
    
    def encode_point(self, point): # turn point into integer indedx
        raise NotImplementedError()
    
    def decode_point_index(self, index): # turn index back into point
        raise NotImplementedError()
    
    def num_points(self): # number of points on the board (area)
        raise NotImplementedError()
    
    def shape(self): # shape of the encoded board structure
        raise NotImplementedError()
# end::base_encoder[]


# tag::encoder_by_name[]
def get_encoder_by_name(name, board_size): # create encoder instances by referencing their name
    if isinstance(board_size, int):
        board_size = (board_size, board_size) # if board size is only 1 intiger, create a square board from it
    module = importlib.import_module('dlgo.encoders.' + name)
    constructor = getattr(module, 'create') # each encoder implementation will have to provide a “create” function that provides an instance
    return constructor
# end::encoder_by_name[]