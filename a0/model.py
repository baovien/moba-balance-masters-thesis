import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F


class Connect2Model(nn.Module):

    def __init__(self, board_size, action_size, device):

        super(Connect2Model, self).__init__()

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
