__all__ = [
    'Agent',
]

class Agent():
    """Interface for a go bot"""
    def select_move(self, game_state):
        raise NotImplementedError()

    def diagnostics(self):
        return {}