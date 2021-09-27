import gzip
import tqdm
n_samples = 0
with gzip.open("data/matches_5148330922-5148330922.gz", 'rt') as fp:
    for line in tqdm.tqdm(fp): 
        n_samples += 1 
    print(n_samples)