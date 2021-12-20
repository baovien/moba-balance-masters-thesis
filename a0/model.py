import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class PreDraftModel:
    pass

class RandomModel():
    def __init__(self, board_size, action_size, device):
        super(RandomModel, self).__init__()
        self.device = device
        self.size = board_size
        self.action_size = action_size

    def forward(self, x):
        action_logits = torch.randn(1, self.action_size, device=self.device)
        value_logit = torch.randn(1, device=self.device)
        return F.softmax(action_logits, dim=1), torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.size)
        with torch.no_grad():
            pi, v = self.forward(board)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]

class DotaDraftModel(nn.Module):

    def __init__(self, board_size, action_size, device):

        super(DotaDraftModel, self).__init__()

        self.device = device
        self.size = board_size
        self.action_size = action_size

        # self.fc1 = nn.Linear(in_features=self.size, out_features=16)
        # self.fc2 = nn.Linear(in_features=16, out_features=16)

        # # Two heads on our network
        # self.action_head = nn.Linear(in_features=16, out_features=self.action_size)
        # self.value_head = nn.Linear(in_features=16, out_features=1)

        self.hidden_dim = 200

        self.embedding_net = nn.Sequential(
          nn.Linear(self.size, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU()
        )

        # Two heads on our network
        self.action_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_size)
        self.value_head = nn.Linear(in_features=self.hidden_dim, out_features=1)

        self.to(device)

    def forward(self, x):
        hidden = self.embedding_net(x)

        action_logits = self.action_head(hidden)
        value_logit = self.value_head(hidden)

        # Return priors for next nodes and value of current node
        return F.softmax(action_logits, dim=1), torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.size)
        self.eval()
        with torch.no_grad():
            pi, v = self.forward(board)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]

# TODO: Fix unpacking in mcts.py 

class BanPickModel(nn.Module):

    def __init__(self, board_size, action_size, device):

        super(BanPickModel, self).__init__()

        self.device = device
        self.size = board_size
        self.action_size = action_size

        # self.fc1 = nn.Linear(in_features=self.size, out_features=16)
        # self.fc2 = nn.Linear(in_features=16, out_features=16)

        # # Two heads on our network
        # self.action_head = nn.Linear(in_features=16, out_features=self.action_size)
        # self.value_head = nn.Linear(in_features=16, out_features=1)

        self.hidden_dim = 200

        self.embedding_net = nn.Sequential(
          nn.Linear(self.size, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim ),
          nn.ReLU()
        )

        # Two heads on our network
        self.pick_action_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_size)
        self.ban_action_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_size)
        self.value_head = nn.Linear(in_features=self.hidden_dim, out_features=1)

        self.to(device)

    def forward(self, x, bans=None):
        hidden = self.embedding_net(x)
                

        pick_action_logits = self.pick_action_head(hidden)
        ban_action_logits = self.ban_action_head(hidden)
        value_logit = self.value_head(hidden)

        if bans:
            pick_action_logits = pick_action_logits * bans
            ban_action_logits = ban_action_logits * bans

        # Return priors for next nodes and value of current node
        return F.softmax(pick_action_logits, dim=1), F.softmax(ban_action_logits, dim=1), torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.size)
        self.eval()
        with torch.no_grad():
            pick_pi, ban_pi, v = self.forward(board)

        return pick_pi.data.cpu().numpy()[0], ban_pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]
