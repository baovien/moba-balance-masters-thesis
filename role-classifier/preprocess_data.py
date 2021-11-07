import os
import json
import numpy as np
import pickle 

if __name__ == "__main__":
    # loop through all the files in data/parsed and unpickle them
    features = []
    
    for filename in os.listdir("data/parsed"):
        with open("data/parsed/" + filename, "rb") as f:
            match = pickle.load(f)
            # get players in the match
            players = match["players"]
            

            
