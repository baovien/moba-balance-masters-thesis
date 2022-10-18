### Master's Thesis
# Lost in Draft: Investigating Game Balance in Multiplayer Online Battle Arena Drafting
https://hdl.handle.net/11250/3026277
## Abstract
The thesis explores modern machine learning solutions to turn-based strategy games. In particular, we explore the possibilities of equalizing the playing field for both teams in the draft phase of Defense of the Ancients 2 (Dota 2) and League of Legends (LoL), with both games being giants in the multi-million dollar esports industry.

The thesis covers the Multiplayer Online Battle Arena video game genre and the draft phase the games use. We also discuss the technology used to address the problem, as well as the basic concepts of modern machine learning that allowed this technology to arise. We then introduce the Win Rate Predictor, which is our implementation of the reward function in the Monte Carlo Tree Search algorithm used to predict the win rate of each team given different parameters in the draft phase.

The results show clear and quantifiable differences in different parts of the draft phase. This includes reordering the pick order, the impact of including banning in the draft phase, and the balance of different draft schemes.

Specifically, first pick has a higher win rate than last pick for the majority of the draft schemes, suggesting that strong initial picks are more valuable than reactive response picks. Additionally, bans can be a way to influence the balance of a draft phase. Our simulations also suggest that the southwestern locations on the map have a higher win rate in both Dota 2 and LoL. And finally, according to our simulations, the games' respective implementation of a draft scheme is the most evenly balanced draft scheme for their game.


## Folder structure
```
📦dota-masters-thesis
 ┣ 📂data               (project data)
 ┣ 📂drafter            (self-play drafter)
 ┣ 📂notebooks          (prototyping/poc)
 ┣ 📂old                (legacy code)
 ┣ 📂position_optimizer (dota2 pos. optim.)
 ┗ 📂scraper            (dota2 scraper)
```

