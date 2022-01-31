from collections import Counter
import numpy as np
from enum import Enum
from virtual_loss import VirtualLossDota, VirtualLossLoL


class Move(Enum):
    PICK = 0
    BAN = 1
    NOP = -1 #NO OPERATION

class Player(Enum):
    P1 = 1
    P2 = -1


drafting_rules = {
    'schoolyard':   [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] * 5 + [(Move.PICK, Player.P1)],
    'schoolyard2':  [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] * 4  + 
                    [(Move.PICK, Player.P2),(Move.PICK, Player.P1)]  + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy


    'captains':     [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 2 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), (Move.PICK, Player.P1)] +
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 3 +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 2 +
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy
    
    # fp has lp
    'captains_fp':     [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 2 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), (Move.PICK, Player.P1)] +
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 3 +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 2 +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy
    

    'captains_no_bans': 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), (Move.PICK, Player.P1)] +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy

    'tournament':   [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 3 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), 
                    (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.BAN, Player.P2), (Move.BAN, Player.P1)] * 2 +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy
    
    'tournament_fp':   [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 3 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), 
                    (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.BAN, Player.P2), (Move.BAN, Player.P1)] * 2 +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P1)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy

    'tournament_no_bans':  
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2), (Move.PICK, Player.P2), 
                    (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] +
                    [(Move.PICK, Player.P2), (Move.PICK, Player.P1), (Move.PICK, Player.P1), (Move.PICK, Player.P2)] + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy

    'hon_captains': 
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 2 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] * 3 + 
                    [(Move.BAN, Player.P1), (Move.BAN, Player.P2)] * 3 + 
                    [(Move.PICK, Player.P1), (Move.PICK, Player.P2)] * 2 + 
                    [(Move.PICK, Player.P1)], # Last one is a dummy
}




class GameState:
    
    @staticmethod
    def picks(board):
        action_size = (board.shape[0] - 3) // 2
        return board[0:action_size]

    @staticmethod
    def bans(board):
        action_size = (board.shape[0] - 3) // 2
        return board[action_size:action_size*2]

    @staticmethod
    def first_pick(board):
        return board[-3]

    @staticmethod
    def radiant_player(board):
        return board[-2]

    @staticmethod
    def move_number(board):
        return board[-1]

    @staticmethod
    def get_legal_moves_for_picks(board):
        picks = GameState.picks(board)
        bans = GameState.bans(board)

        a = (picks == 0).astype(int) * bans
        b = np.zeros(board.shape[0] - 3)  # legal moves should be n_heroes * 2 - 2
        b[:picks.shape[0]] = a
        
        return b

    @staticmethod
    def get_legal_moves_for_bans(board):
        picks = GameState.picks(board)
        bans = GameState.bans(board)

        a = (picks == 0).astype(int) * bans
        b = np.zeros(board.shape[0] - 3)
        b[picks.shape[0]: picks.shape[0] * 2] = a 
        
        return b

    @staticmethod
    def coin_flip(board):
        b = np.copy(board)
        b[-3] = np.random.choice([1, -1])
        b[-2] = np.random.choice([1, -1])
        
        return b

class Dota2Game:
    def __init__(self, draft_type):
        self.n_heroes = 121
        self.columns = 245 # n_heroes * 2 + 1 (first_pick) +  1 (radiant_player)
        self.draft_actions = drafting_rules[draft_type]
        self.vl = VirtualLossDota()
        self.game_rules = GameState()

    def get_init_board(self):
        b = np.zeros((self.columns,), dtype=np.int)
        
        # init bans with ones
        b[self.n_heroes:self.n_heroes*2] = 1

        # randomize who starts first pick and who is radiant
        board = self.game_rules.coin_flip(b)

        # set move number to 0
        board[-1] = 0
        return board

    def get_board_size(self):
        return self.columns - 1

    def get_action_size(self):
        return self.n_heroes

    def get_next_state(self, board, player, action):
        b = board.copy()
        move_number = self.game_rules.move_number(board)
        draft_action, player_to_move = self.draft_actions[move_number]

        # print("move:", move_number, "draft_action:", draft_action , "action: ", action, "player:", player_to_move)
        
        if draft_action == Move.PICK:
            b[action] = 1 * player
        elif draft_action == Move.BAN: 
            b[action] = 0  
        else:
            raise Exception("Invalid draft action")

        # if self.is_terminal(b):
        #     return (self.get_canonical_board(b, player), 1)

        _, next_player_to_move  = self.draft_actions[move_number + 1]
        # increment move number
        b[-1] += 1

        if player_to_move == next_player_to_move:
            return (b, player)
        else:
            return (b, -player)


    def get_valid_moves(self, board):
        # All moves are valid by default, picks = 0s, bans = 1s
        move_number = self.game_rules.move_number(board)
        draft_action, _= self.draft_actions[move_number]
        if draft_action == Move.PICK:
            return self.game_rules.get_legal_moves_for_picks(board)
        elif draft_action == Move.BAN:
            return self.game_rules.get_legal_moves_for_bans(board)

    def is_terminal(self, board):
        picks = self.game_rules.picks(board)
        t0 = (picks == 1).sum() == 5
        t1 = (picks == -1).sum() == 5
        
        return t0 and t1

        # return np.abs(self.game_rules.picks(board)).sum() == 10

    def virtual_loss(self, board, player):
        winner, probas = self.vl(GameState.picks(board))
        if winner and player == 1:
            return 1 
        elif not winner and player == -1:
            return 1
        return -1

    def get_reward_for_player(self, board, player):
        # return None if not ended 
        # virtual loss if player 1 wins
        # 1 - virtual loss if player 1 lost
        
        if self.is_terminal(board):
            return self.virtual_loss(board, player)
        return None

    def get_canonical_board(self, board, player):
        picks = self.game_rules.picks(board)
        bans = self.game_rules.bans(board)
        first_pick = self.game_rules.first_pick(board)
        radiant_player = self.game_rules.radiant_player(board)
        move_number = self.game_rules.move_number(board)

        # if player is same as current, return same player
        # if player 2, flip

        return np.concatenate((picks * player, bans, [first_pick * player], [radiant_player * player], [move_number]))
        

class LoLGame:
    def __init__(self, draft_type):
        self.n_heroes = 156
        self.columns = (156*2)+3 # n_heroes * 2 + 1 (first_pick) +  1 (radiant_player) +  1 move_number 
        self.draft_actions = drafting_rules[draft_type]
        self.vl = VirtualLossLoL()
        self.game_rules = GameState()

    def get_init_board(self):
        b = np.zeros((self.columns,), dtype=np.int)
        
        # init bans with ones
        b[self.n_heroes:self.n_heroes*2] = 1

        # randomize who starts first pick and who is radiant
        board = self.game_rules.coin_flip(b)

        # set move number to 0
        board[-1] = 0
        return board

    def get_board_size(self):
        return self.columns - 1

    def get_action_size(self):
        return self.n_heroes

    def get_next_state(self, board, player, action):
        b = board.copy()

        move_number = self.game_rules.move_number(board)
        draft_action, player_to_move = self.draft_actions[move_number]

        # print("move:", move_number, "draft_action:", draft_action , "action: ", action, "player:", player_to_move)
        
        if draft_action == Move.PICK:
            b[action] = 1 * player
        elif draft_action == Move.BAN: 
            b[action] = 0  
        else:
            raise Exception("Invalid draft action")

        _, next_player_to_move  = self.draft_actions[move_number + 1]
        # increment move number
        b[-1] += 1

        if player_to_move == next_player_to_move:
            return (b, player)
        else:
            return (b, -player)


    def get_valid_moves(self, board):
        # All moves are valid by default, picks = 0s, bans = 1s
        move_number = self.game_rules.move_number(board)
        draft_action, _= self.draft_actions[move_number]
        if draft_action == Move.PICK:
            return self.game_rules.get_legal_moves_for_picks(board)
        elif draft_action == Move.BAN:
            return self.game_rules.get_legal_moves_for_bans(board)

    def is_terminal(self, board):
        picks = self.game_rules.picks(board)
        t0 = (picks == 1).sum() == 5
        t1 = (picks == -1).sum() == 5
        return t0 and t1


    def virtual_loss(self, board, player):
        winner, probas = self.vl(GameState.picks(board))
        
        if winner and player == 1:
            return 1 
        elif not winner and player == -1:
            return 1

        return -1

    def get_reward_for_player(self, board, player):
        # return None if not ended 
        # virtual loss if player 1 wins
        # 1 - virtual loss if player 1 lost
        
        if self.is_terminal(board):
            return self.virtual_loss(board, player)
        return None

    def get_canonical_board(self, board, player):
        picks = self.game_rules.picks(board)
        bans = self.game_rules.bans(board)
        first_pick = self.game_rules.first_pick(board)
        radiant_player = self.game_rules.radiant_player(board)
        move_number = self.game_rules.move_number(board)

        # if player is same as current, return same player
        # if player 2, flip

        return np.concatenate((picks * player, bans, [first_pick * player], [radiant_player * player], [move_number]))
