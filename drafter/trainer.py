import os
import numpy as np
from random import shuffle
import uuid
import torch
import torch.optim as optim
import pickle
import tqdm
from model import RandomModel
from game import Dota2Game
from monte_carlo_tree_search import MCTS
from utils import idx_to_name
class Trainer:
    def __init__(self, game, model, args, temperature=1, epsilon_greedy=None):
        self.game = game
        self.model = model
        self.args = args
        self.temperature = temperature
        self.epsilon_greedy = epsilon_greedy
        self.run_id = str(uuid.uuid4())
        # self.mcts = MCTS(self.game, self.model, self.args, self.epsilon_greedy)

    def exceute_episode(self):
        train_examples = []
        current_player = 1
        state = self.game.get_init_board()
        # actions = []
        while True:
            canonical_board = self.game.get_canonical_board(state, current_player)

            mcts = MCTS(self.game, self.model, self.args, self.epsilon_greedy)
            root = mcts.run(self.model, canonical_board, to_play=1)

            # action_probs = [0 for _ in range(self.game.get_action_size())]
            action_probs = np.zeros(self.game.get_action_size() * 2) # *2 bc we have actions for picks and bans

            for k, v in root.children.items():
                action_probs[k] = v.visit_count

            action_probs = action_probs / np.sum(action_probs)
            train_examples.append((canonical_board[:-1], current_player, action_probs)) # remove move_count from state

            action = root.select_action(temperature=self.temperature)
            state, current_player = self.game.get_next_state(state, current_player, action)
            reward = self.game.get_reward_for_player(state, current_player)
            # actions.append(idx_to_name(action, "dota"))

            if reward is not None:
                # print(actions, reward)
                ret = []
                for hist_state, hist_current_player, hist_action_probs in train_examples:
                    # [Board, currentPlayer, actionProbabilities, Reward]
                    ret.append((hist_state, hist_action_probs, reward * ((-1) ** (hist_current_player != current_player))))

                return ret

    def learn(self):
        for i in tqdm.tqdm(range(1, self.args['numIters'] + 1), desc="Interation"):
            train_examples = []

            # generate training examples
            for eps in tqdm.tqdm(range(self.args['numEps']), desc="Episode"):
                iteration_train_examples = self.exceute_episode()
                train_examples.extend(iteration_train_examples)

            shuffle(train_examples)
            self._save_training_data(train_examples, i)
            if isinstance(self.model, RandomModel):
                continue
            _ = self.train(train_examples)
            folder = self.args['checkpoint_path']
            filename = "checkpoint_{}.pth".format(i)
            self.save_checkpoint(folder=folder, filename=filename)



    def train(self, examples): 
        optimizer = optim.Adam(self.model.parameters(), lr=5e-4)
        pi_losses = []
        v_losses = []

        for epoch in range(self.args['epochs']):
            self.model.train()

            batch_idx = 0

            while batch_idx < int(len(examples) / self.args['batch_size']):
                sample_ids = np.random.randint(len(examples), size=self.args['batch_size'])
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                boards = torch.FloatTensor(np.array(boards).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict
                boards = boards.contiguous().cuda()
                target_pis = target_pis.contiguous().cuda()
                target_vs = target_vs.contiguous().cuda()

                # compute output
                out_pi, out_v = self.model(boards)
                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v
                
                if torch.isnan(out_pi[0]).any() or torch.isnan(out_v[0]).any():
                    print('NaN detected')
                    continue

                pi_losses.append(float(l_pi))
                v_losses.append(float(l_v))

                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                batch_idx += 1

            # print()
            # print("Policy Loss", np.mean(pi_losses))
            # print("Value Loss", np.mean(v_losses))
            # print("Examples:")
            # print(out_pi[0].detach())   
            # print(target_pis[0])

            if torch.isnan(out_pi[0]).any():
                print("out_pi contains nan")
                break

            if torch.isnan(target_pis[0]).any():
                print("out_v contains nan")
                break

        losses = {
                'pi_losses': pi_losses,
                'v_losses': v_losses
            }

        return losses

    def loss_pi(self, targets, outputs):
        loss = -(targets * torch.log(outputs)).sum(dim=1)
        return loss.mean()

    def loss_v(self, targets, outputs):
        loss = torch.sum((targets-outputs.view(-1))**2)/targets.size()[0]
        return loss

    def save_losses(self, losses, folder, filename):
        with open(os.path.join(folder, filename), 'wb') as f:
            pickle.dump(losses, f)

    def save_checkpoint(self, folder, filename):
        if not os.path.exists(folder):
            os.mkdir(folder)

        filepath = os.path.join(folder, filename)
        torch.save({
            'state_dict': self.model.state_dict(),
        }, filepath)


    def _save_training_data(self, train_examples, it_num):
        folder = self.args['training_data_path']
        if not os.path.exists(folder):
            os.mkdir(folder)

        filepath = os.path.join(folder, '{}_{}.pkl'.format(self.run_id, it_num))

        with open(filepath, 'wb') as f:
            pickle.dump(train_examples, f)