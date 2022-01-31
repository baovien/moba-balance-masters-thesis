import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

class PreDraftModel:
    pass

class RandomModel(nn.Module):
    def __init__(self, board_size, action_size, device):
        super(RandomModel, self).__init__()
        self.device = device
        self.size = board_size
        self.action_size = action_size

    def eval(self):
        pass

    def train(self):
        pass

    def __repr__(self) -> str:
        return "RandomModel"

    def forward(self, x):
        # action_logits = torch.randn(1, self.action_size, device=self.device)
        # action_logits2 = torch.randn(1, self.action_size, device=self.device)
        # value_logit = torch.randn(1, device=self.device)
        action_logits = torch.full((1, self.action_size), 0.5, device=self.device)
        action_logits2 = torch.full((1, self.action_size), 0.5, device=self.device)
        value_logit = torch.randn(1, device=self.device)

        concat_logits = torch.cat((action_logits, action_logits2), dim=1)

        return F.softmax(concat_logits, dim=1), torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.size)
        with torch.no_grad():
            pi, v = self.forward(board)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]

class DotaDraftModel(nn.Module):

    def __init__(self, input_dims, action_dims, device):

        super(DotaDraftModel, self).__init__()

        self.device = device
        self.input_dims = input_dims
        self.action_dims = action_dims
        self.hidden_dim = 300 # TODO: set to 768 on final train

        self.embedding_net = nn.Sequential(
          nn.Linear(self.input_dims, self.hidden_dim),
        #   nn.BatchNorm1d(self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU()
        ) # maybe add batchnorm to normalize, as the inputs vary a lot

        # Two heads on our network
        self.action_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_dims)
        self.action2_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_dims)
        self.value_head = nn.Linear(in_features=self.hidden_dim, out_features=1)

        self.to(device)

    def __repr__(self):
        return "DotaDraftModel"

    def forward(self, x):
        hidden = self.embedding_net(x)

        action_logits = self.action_head(hidden)
        action2_logits = self.action2_head(hidden)
        value_logit = self.value_head(hidden)

        a_probs = F.softmax(action_logits, dim=1)
        a2_probs = F.softmax(action2_logits, dim=1)
        action_probs = torch.cat((a_probs, a2_probs), dim=1)
        # Return priors for next nodes and value of current node
        return action_probs, torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.input_dims)
        self.eval()
        with torch.no_grad():
            pi, v = self.forward(board)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]


class LoLDraftModel(nn.Module):

    def __init__(self, input_dims, action_dims, device):

        super(LoLDraftModel, self).__init__()

        self.device = device
        self.input_dims = input_dims
        self.action_dims = action_dims
        self.hidden_dim = 768 # TODO: set to 768 on final train

        self.embedding_net = nn.Sequential(
          nn.Linear(self.input_dims, self.hidden_dim),
          nn.BatchNorm1d(self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU()
        ) # maybe add batchnorm to normalize, as the inputs vary a lot

        # Two heads on our network
        self.action_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_dims)
        self.action2_head = nn.Linear(in_features=self.hidden_dim, out_features=self.action_dims)
        self.value_head = nn.Linear(in_features=self.hidden_dim, out_features=1)

        self.to(device)

    def __repr__(self):
        return "LoLDraftModel"

    def forward(self, x):
        hidden = self.embedding_net(x)

        action_logits = self.action_head(hidden)
        action2_logits = self.action2_head(hidden)
        value_logit = self.value_head(hidden)

        a_probs = F.softmax(action_logits, dim=1)
        a2_probs = F.softmax(action2_logits, dim=1)
        action_probs = torch.cat((a_probs, a2_probs), dim=1)
        # Return priors for next nodes and value of current node
        return action_probs, torch.tanh(value_logit)

    def predict(self, board):
        board = torch.FloatTensor(board.astype(np.float32)).to(self.device)
        board = board.view(1, self.input_dims)
        self.eval()
        with torch.no_grad():
            pi, v = self.forward(board)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]
