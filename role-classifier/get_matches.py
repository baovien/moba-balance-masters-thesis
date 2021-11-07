'''
One of the latest match ids BEFORE patch 7.30e: 6237281052
Use this id to get a list of parsed matches from api.opendota.com.
api_key = 8a0ef958-a013-405a-b419-8c7cbb4e393a
'''

import json
import pickle
import tqdm
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

if __name__ == "__main__":
    print(f"starting")
    with open("data/match_ids.json", 'r') as fp:
        match_ids = json.load(fp)

    idx = 0
    with FuturesSession() as session:
        futures = [session.get("https://api.opendota.com/api/matches/{}?api_key=8a0ef958-a013-405a-b419-8c7cbb4e393a".format(str(match_id))) for match_id in tqdm.tqdm(match_ids[0:])]
        for future in tqdm.tqdm(as_completed(futures)):
            response = future.result()
            try:
                match = response.json()

                if "error" in match:
                    continue

                outf = "data/parsed/{}.pkl".format(idx)

                with open(outf, "wb") as f:
                    pickle.dump(match, f, protocol=pickle.HIGHEST_PROTOCOL)
                    # f.write(json.dumps(match))
                idx += 1
            except Exception as e:
                print(e)
                print(response)
                

    print("done")




