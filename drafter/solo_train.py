from collections import defaultdict
import os
from random import shuffle
import torch
import tqdm

from game import Dota2Game
from model import DotaDraftModel
from trainer import Trainer
import glob
import pickle

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    args = {
        'batch_size': 4096,
        'epochs': 20,                                   # Number of epochs of training per iteration
        'checkpoint_path': 'checkpoints/delta2/',                   # location to save latest set of weights
        'training_data_path': 'training_data/',         # location to save training data
        'draft_type': 'captains',
    }

    game = Dota2Game(draft_type=args['draft_type'])
    board_size = game.get_board_size()
    action_size = game.get_action_size()

    model = DotaDraftModel(board_size, action_size, device)

    print("args:", args)

    training_examples = []
    tot_losses = defaultdict(list)
    # read training example pkl and extend training_examples
    print("started training")

    query = os.path.join(args["training_data_path"], "**", "*.pkl")
    trainer = Trainer(game, model, args, temperature=1, epsilon_greedy=None) # only mcts use epsilon
    folder = args['checkpoint_path']
    # save checkpoint every 100 file
    for i, file in enumerate(tqdm.tqdm(glob.glob(query, recursive=True))):
    # for file in tqdm.tqdm(glob.iglob(query, recursive=True)):
        with open(file, 'rb') as f:
            if i % 100 == 0:
                print("saving checkpoint at {}".format(i))
                filename = "delta2_{}.pth".format(i)
                trainer.save_checkpoint(folder, filename)
                trainer.save_losses(tot_losses, folder=folder, filename='losses_{}.pkl'.format(i))    

            training_examples = pickle.load(f)
            shuffle(training_examples)
            losses = trainer.train(training_examples)
            tot_losses["pi_losses"].extend(losses["pi_losses"])
            tot_losses["v_losses"].extend(losses["v_losses"])

    print("saving checkpoint at {}".format(i))
    filename = "delta2_{}.pth".format(i)
    trainer.save_checkpoint(folder, filename)
    trainer.save_losses(tot_losses, folder=folder, filename='losses_{}.pkl'.format(i))
    # save losses
    
    print("jobs done!")