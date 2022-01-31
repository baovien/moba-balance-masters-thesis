import os
import argparse

# python main.py --device 1 --modelname alpha10 --game dota --draft captains_no_bans --batch_size 4096 -s 200
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-b','--batch_size', help='Batch Size. Default=64', type=int, default=64)
parser.add_argument('-i','--iters', help='Number of iterations. Default=1000', type=int, default=500)
parser.add_argument('-e','--episodes', help='Episodes. Default=500', type=int, default=500)
parser.add_argument('-s','--simulations', help='Number of simulations. Default=50', type=int, default=50)
parser.add_argument('-p','--epochs', help='Epochs. Default=2', type=int, default=2)
parser.add_argument('-d','--draft', help='Draft Type', type=str, default="captains")
parser.add_argument('-g','--game', help='Game', choices=["dota", "lol"], type=str, required=True)
parser.add_argument('-c','--device', help='CUDA device', choices=['0','1'], type=str, required=True)
parser.add_argument('-n','--modelname', help='Model name', type=str, required=True)
parser.add_argument('-m','--model', help='NN model', type=str,choices=["linear", "random"],  required=True)
parser.add_argument('-t','--temperature', help='Temperature', type=int, default=1)

args = vars(parser.parse_args())
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = args['device']

from game import Dota2Game, LoLGame
from model import DotaDraftModel, RandomModel
from trainer import Trainer
import torch

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("running on device: {}".format(device))
    print(args)

    model_checkpoint_path = "checkpoints/{}_{}_{}".format(args['modelname'], args['game'] ,args['draft'])
    training_data_path = "training_data/{}_{}_{}".format(args['modelname'], args['game'] ,args['draft'])

    train_args = {
        'batch_size': args['batch_size'],
        'numIters': args['iters'],                           # Total number of training iterations
        'num_simulations': args['simulations'],                          # Total number of MCTS simulations to run when deciding on a move to play
        'numEps': args['episodes'],                                  # Number of full games (episodes) to run during each iteration
        'numItersForTrainExamplesHistory': 20,          # Maximum number of 'iterations' that game episodes are kept in queue. After that last is popped and new one is added.
        'epochs': args['epochs'],                                   # Number of epochs of training per iteration
        'checkpoint_path': model_checkpoint_path,        # location to save latest set of weights
        'training_data_path': training_data_path,         # location to save training data
        'draft_type': args['draft'],
    }

    if args['game'] == "dota":
        game = Dota2Game(draft_type=train_args['draft_type'])
    elif args['game'] == "lol":
        game = LoLGame(draft_type=train_args['draft_type'])
    else:
        raise ValueError("Invalid game")

    board_size = game.get_board_size()
    action_size = game.get_action_size()

    if args['model'] == "linear":
        model = DotaDraftModel(board_size, action_size, device)
    elif args['model'] == "random":
        model = RandomModel(board_size, action_size, device)
    else:
        raise ValueError("Invalid model")

    trainer = Trainer(game, model, train_args, temperature=1, epsilon_greedy=0.2)
    trainer.learn()
