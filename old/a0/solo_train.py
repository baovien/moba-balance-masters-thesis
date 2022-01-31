import torch

from game import Dota2Game
from model import DotaDraftModel
from trainer import Trainer
import glob
import pickle

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # add args for checpoints and that below

    args = {
        'batch_size': 64,
        'numIters': 1000, #500                           # Total number of training iterations
        'num_simulations': 100,                          # Total number of MCTS simulations to run when deciding on a move to play
        'numEps': 500,                                  # Number of full games (episodes) to run during each iteration
        'numItersForTrainExamplesHistory': 20,          # Maximum number of 'iterations' that game episodes are kept in queue. After that last is popped and new one is added.
        'epochs': 10,                                   # Number of epochs of training per iteration
        'checkpoint_path': 'alpha8/',                   # location to save latest set of weights
        'training_data_path': 'training_data/',         # location to save training data
        'draft_type': 'school_yard',
    }

    game = Dota2Game(draft_type=args['draft_type'])
    board_size = game.get_board_size()
    action_size = game.get_action_size()

    model = DotaDraftModel(board_size, action_size, device)

    print("args:", args)


    training_examples = []

    # read training example pkl and extend training_examples
    for file in glob.glob(args['training_data_path'] + '*.pkl'):
        with open(file, 'rb') as f:
            training_examples.extend(pickle.load(f))

    print('training examples:', len(training_examples))

    trainer = Trainer(game, model, args, epsilon_greedy=0.5)
    trainer.train(training_examples)
    folder = args['checkpoint_path']
    filename = "alpha8.pth"
    trainer.save_checkpoint(folder=folder, filename=filename)

    print("save checkpoint to:", folder + filename)
    print("done!")