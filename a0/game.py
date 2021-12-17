import numpy as np
import random
import pickle


hero_coefs = np.random.uniform(low=-1, high=1, size=(121,))

class Dota2Game:
    """
    A very, very simple game of ConnectX in which we have:
        rows: 1
        columns: 4
        winNumber: 2
    """

    def __init__(self):
        self.columns = 121
        self.picks = 10

    def get_init_board(self):
        b = np.zeros((self.columns,), dtype=np.int)
        return b

    def get_board_size(self):
        return self.columns

    def get_action_size(self):
        return self.columns

    def get_next_state(self, board, player, action):
        b = np.copy(board)
        b[action] = player

        # Return the new game, but
        # change the perspective of the game with negative
        return (b, -player)

    def get_valid_moves(self, board):
        # All moves are invalid by default
        return (board == 0).astype(np.int)

    def is_terminal(self, board):
        return np.abs(board).sum() == 10

    def virtual_loss(self, board):
        # TODO: investigate board negation vs player turn 
        
        pred = hero_coefs.dot(board)
        if pred > 0:
            return 1 
    
        return -1

    def get_reward_for_player(self, board, player):
        # return None if not ended 
        # virtual loss if player 1 wins
        # 1 - virtual loss if player 1 lost
        
        if self.is_terminal(board):
            if player == 1:
                return self.virtual_loss(board)
            elif player == -1:
                return -self.virtual_loss(board)

        return None

    def get_canonical_board(self, board, player):
        return player * board

    def encode_board(self, board):
        t0 = [k for k, v in enumerate(board) if v == 1]
        t1 = [k for k, v in enumerate(board) if v == -1]
        return t0, t1
        # find what positions the players have played 
    



    def _load_vl(self):
        with open('vl_logreg_57.pkl', 'rb') as f:
            self.model = pickle.load(f)





class Connect2Game:
    """
    A very, very simple game of ConnectX in which we have:
        rows: 1
        columns: 4
        winNumber: 2
    """

    def __init__(self):
        self.columns = 4
        self.win = 2

    def get_init_board(self):
        b = np.zeros((self.columns,), dtype=np.int)
        return b

    def get_board_size(self):
        return self.columns

    def get_action_size(self):
        return self.columns

    def get_next_state(self, board, player, action):
        b = np.copy(board)
        b[action] = player

        # Return the new game, but
        # change the perspective of the game with negative
        return (b, -player)

    def has_legal_moves(self, board):
        for index in range(self.columns):
            if board[index] == 0:
                return True
        return False

    def get_valid_moves(self, board):
        # All moves are invalid by default
        valid_moves = [0] * self.get_action_size()

        for index in range(self.columns):
            if board[index] == 0:
                valid_moves[index] = 1

        return valid_moves

    def is_win(self, board, player):
        count = 0
        for index in range(self.columns):
            if board[index] == player:
                count = count + 1
            else:
                count = 0

            if count == self.win:
                return True

        return False

    def get_reward_for_player(self, board, player):
        # return None if not ended, 1 if player 1 wins, -1 if player 1 lost

        if self.is_win(board, player):
            return 1
        if self.is_win(board, -player):
            return -1
        if self.has_legal_moves(board):
            return None

        return 0

    def get_canonical_board(self, board, player):
        return player * board

