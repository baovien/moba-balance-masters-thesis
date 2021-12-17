import os
import numpy as np

class VirtualLoss:
    def __init__(self):
        self.hero_pos_dist = self._load_hero_pos()

    def get_draft_pos(self, draft):
        # team = 121 where 1 is radiant and -1 is dire
        t0 = np.where(draft == 1)[0]
        t1 = np.where(draft == -1)[0]
        
        t0_dist = np.vstack([self.hero_pos_dist[k] for k in t0])
        t1_dist = np.vstack([self.hero_pos_dist[k] for k in t1])

        t0_pos = np.zeros(5, dtype=int)
        t1_pos = np.zeros(5, dtype=int)

        print(t0)

        tmp = t0_dist.copy()

        for i in range(5):
            hero, pos = np.unravel_index(tmp.argmax(), tmp.shape)
            tmp[hero,:] = -np.inf
            tmp[:,pos] = -np.inf
            t0_pos[hero] = pos

        print("")

        print(t1)

        tmp2 = t1_dist.copy()

        for i in range(5):
            hero, pos = np.unravel_index(tmp2.argmax(), tmp2.shape)
            tmp2[hero,:] = -np.inf
            tmp2[:,pos] = -np.inf
            t1_pos[hero] = pos

        print(t0_pos, t1_pos)



    def _load_hero_pos(self):
        assert os.path.isfile('hero_roles.npy')
    
        hero_roles = np.load('hero_roles.npy')
        
        z = hero_roles.sum(axis=1)
        return hero_roles / z[:,None] 


if __name__ == "__main__":
    vl = VirtualLoss()

    draft = np.array([-1, -1, -1,  1, -1,  1, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
         0,  0])

    vl.get_draft_pos(draft)




