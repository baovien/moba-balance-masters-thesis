import os
import json
import numpy as np
import pickle
class VirtualLoss:
    def __init__(self):
        self.hero_pos_dist = self._load_hero_pos()
        self.heroes_info = self._load_heroes_info()
        self.model = self._load_model()

    def get_draft_pos(self, draft):
        # team = 121 where 1 is radiant and -1 is dire
        t0 = np.where(draft == 1)[0]
        t1 = np.where(draft == -1)[0]
        
        t0_dist = np.vstack([self.hero_pos_dist[k] for k in t0])
        t1_dist = np.vstack([self.hero_pos_dist[k] for k in t1])

        t0_pos = np.zeros(5, dtype=int)
        t1_pos = np.zeros(5, dtype=int)


        tmp = t0_dist.copy()

        for _ in range(5):
            hero, pos = np.unravel_index(tmp.argmax(), tmp.shape)
            tmp[hero,:] = -np.inf
            tmp[:,pos] = -np.inf
            t0_pos[hero] = pos

        tmp2 = t1_dist.copy()

        for _ in range(5):
            hero, pos = np.unravel_index(tmp2.argmax(), tmp2.shape)
            tmp2[hero,:] = -np.inf
            tmp2[:,pos] = -np.inf
            t1_pos[hero] = pos


        # print([(self.idx_to_name_and_id(k), pos) for k, pos in zip(t0, t0_pos)])
        # print([(self.idx_to_name_and_id(k), pos) for k, pos in zip(t1, t1_pos)])
        return t0, t1, t0_pos, t1_pos

    def __call__(self, board):
        enc = self._encode_board(board)

        return self.model.predict(enc.reshape(1, -1))[0], self.model.predict_proba(enc.reshape(1, -1))[0]

    def _load_model(self):
        with open('data/vl_logreg_57.pkl', 'rb') as f:
            return pickle.load(f)


    def _encode_board(self, board):
        """
        encode board shape 121 to 605 
        """
        t0, t1, t0_pos, t1_pos = self.get_draft_pos(board)
        draft_encoded_pos = np.zeros(605, dtype=int)
        teams_concat = np.concatenate((t0, t1))
        teams_pos_concat = np.concatenate((t0_pos, t1_pos))
        for k, i in enumerate(teams_concat):
            hero_pos = teams_pos_concat[k]
            if k > 4:
                draft_encoded_pos[i*5+hero_pos] = -1
            else: 
                draft_encoded_pos[i*5 + hero_pos] = 1
        
        return draft_encoded_pos

    def idx_to_name_and_id(self, idx):
        return self.heroes_info[idx]['localized_name']

    def name_to_idx(self, name):
        for i, v in enumerate(self.heroes_info):
            if v['localized_name'] == name:
                return int(i)

    def _load_heroes_info(self):
        assert os.path.isfile('data/heroes.json')
        with open('data/heroes.json', 'r') as f:
            return json.load(f)

    def _load_hero_pos(self):
        assert os.path.isfile('data/hero_roles.npy')
    
        hero_roles = np.load('data/hero_roles.npy')
        
        z = hero_roles.sum(axis=1)
        return hero_roles / z[:,None] 


if __name__ == "__main__":
    vl = VirtualLoss()

    # draft = np.zeros(121, dtype=int)
    # draft[0:5] = 1
    # draft[5:10] = -1
    # print(draft)
    t0 = ['Hoodwink', 'Silencer', 'Chaos Knight',  'Sniper',  'Necrophos']
    t1 = ['Skywrath Mage', 'Phantom Assassin', 'Mirana', 'Venomancer', 'Invoker']

    t0_idx = [vl.name_to_idx(k) for k in t0]
    t1_idx = [vl.name_to_idx(k) for k in t1]

    draft_test = np.zeros(121, dtype=int)
    draft_test[t0_idx] = 1 
    draft_test[t1_idx] = -1

    # print(vl.get_draft_pos(draft_test))
    print(t0_idx, t1_idx)
    print(vl._encode_board(draft_test))


    # enc = vl._encode_board(draft)


    win_loss = vl(draft_test)
    print(win_loss)


