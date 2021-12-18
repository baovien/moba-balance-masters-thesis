import torch

from game import Connect2Game, Dota2Game
from model import Connect2Model
from trainer import Trainer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# add args for checpoints and that below

args = {
    'batch_size': 64,
    'numIters': 500, #500                                # Total number of training iterations
    'num_simulations': 200,                         # Total number of MCTS simulations to run when deciding on a move to play
    'numEps': 150,                                  # Number of full games (episodes) to run during each iteration
    'numItersForTrainExamplesHistory': 20,
    'epochs': 2,                                    # Number of epochs of training per iteration
    'checkpoint_path': 'checkpoints2/',                # location to save latest set of weights
    'training_data_path': 'training_data/',         # location to save training data
}

game = Dota2Game()
board_size = game.get_board_size()
action_size = game.get_action_size()

model = Connect2Model(board_size, action_size, device)

trainer = Trainer(game, model, args)
trainer.learn()
