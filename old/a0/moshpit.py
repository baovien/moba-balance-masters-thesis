import torch
from model import DotaDraftModel
from game import Dota2Game
from virtual_loss import VirtualLoss
import numpy as np

if __name__ == "__main__":
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    game = Dota2Game()
    board_size = game.get_board_size()
    action_size = game.get_action_size()

    model = DotaDraftModel(board_size, action_size, device)
    model.load_state_dict(torch.load('checkpoints/checkpoint_iter_210.pth')["state_dict"])

    model2 = DotaDraftModel(board_size, action_size, device)
    model2.load_state_dict(torch.load('checkpoints2/checkpoint_iter_500.pth')["state_dict"])

    vl = VirtualLoss()
    t0 = ['Hoodwink', 'Silencer', 'Chaos Knight',  'Sniper']
    t1 = ['Skywrath Mage', 'Phantom Assassin', 'Mirana', 'Venomancer', 'Invoker']

    t0_idx = [vl.name_to_idx(k) for k in t0]
    t1_idx = [vl.name_to_idx(k) for k in t1]

    draft_test = np.zeros(121, dtype=int)
    draft_test[t0_idx] = 1 
    draft_test[t1_idx] = -1



    pred = model.predict(draft_test)

    print(vl.idx_to_name_and_id(np.argmax(pred[0])), np.max(pred[0]))