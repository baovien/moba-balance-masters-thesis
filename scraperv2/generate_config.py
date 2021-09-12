import sys
import json
import argparse
from collections import defaultdict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate new sequence intervals and write to config.json")
    parser.add_argument('-s','--starting-seq', help='Starting sequence', required=True)
    parser.add_argument('-n','--n-chunks', help='Number of chunks', default=5, required=False)
    parser.add_argument('-i','--interval-size', help='Number of sequences per block', default=2000000, required=False)
    args = vars(parser.parse_args())

    config = defaultdict(list)
    start_seq = int(args["starting_seq"])
    previous_seq = start_seq
    interval_size = int(args["interval_size"])
    n_chunks = args["n_chunks"]

    for _ in range(n_chunks):
        next_seq = previous_seq + interval_size
        seq_range = [previous_seq + 1, next_seq]
        previous_seq = next_seq
        config["ranges"].append(seq_range)

    with open("config.json", "w") as fp: 
        json.dump(config, fp)

    print("Generated new config file with:")
    print(f">   start seq: {start_seq}")
    print(f">   interval:  {interval_size}")
    print(f">   n_chunks:  {n_chunks}")
    sys.exit(0)


