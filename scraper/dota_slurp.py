"""
Borrowed script from WibiDota

start: 
match id 6150000000 
seq num 5146330922 (Tuesday, August 24, 2021 1:03:20 PM)
scraping from patch 7.30 (2 mill)
"""

try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json
import gzip
import logging
import os
import requests
import sys
import time
import datetime
# import signal
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.environ.get("STEAM_API_KEY")

# Time to wait between requests to the dota 2 web API. Number of seconds.
REQUEST_PERIOD = 1.0
# Global that tracks the next time we can make a request.
NEXT_REQUEST_TIME = 0

# The config file we use to store/restore our place between runs and the
# globals for its settings.
CONFIG_FILE = "config.json"

# These globals are for calculating aggregate performance numbers for the time
# we spend waiting between requests.
TOTAL_WAIT_TIME = 0.0
TOTAL_CALLS = 0

ERROR_SLEEP_TIME = 60 * 1

# Number of sequence numbers to have covered before printing
# a log message
LOG_INTERVAL = 5000

MATCHES_PER_REQUEST = 100

WAIT_TIMES = [10, 60, 120, 5 * 60, 5 * 60, 10 * 60, 15 * 60, 30 * 60]

def make_url(seq_num): 
    return "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v1?key={}&start_at_match_seq_num={}&matches_requested={}&skill=3&min_players=10".format(API_KEY, seq_num, MATCHES_PER_REQUEST)


def recover(filename):
    """
    Attempts to retrieve the last sequence number stored in filename, assumed to be a
    plain file of json encoded dota matches. If the file or json is damaged will attempt
    to recover the file by truncating the damaged line
    """
    try:
        f = open(filename, 'r+')
    except IOError:
        return None
    print("{} already exists, recovering last sequence number".format(filename))
    seq = 0
    attempts = 5
    for attempt in range(attempts):
        # typically a line is roughly 10000 bytes, seek ten times that from
        # the back of the file to make sure we do start in the middle of
        # the last line
        try:
            f.seek(-100000, 2)
        except IOError:
            # The file is short, just scan from the top
            f.seek(0, 0)

        # Iterate until we find the last line, track the position
        # that line starts from so we can remove it if we need to
        prev_start = None
        prev_line = None
        start = f.tell()
        line = f.readline()
        if(line == ""):
            print("File was empty, rewriting it")
            f.truncate()
            f.close()
            return None
        while(line != ""):
            prev_start = start
            start = f.tell()
            prev_line = line
            line = f.readline()
        try:
            seq = json.loads(prev_line)['match_seq_num']
            print("Last sequence number saved was {}".format(seq))
            f.close()
            return seq
        except ValueError:
            # Truncate the last line and try again
            print("File damaged, deleting last line and trying again")
            f.seek(prev_start, 0)
            f.truncate()
    print("File could not be recovered in {}  attempts, exiting".format(attempts))
    f.close()
    exit(-1)


def read_config():
    """
    Reads in the starting point, block size, and step value from a json config file.
    """
    global NEXT_SEQ, BLOCK_SIZE, NUM_SKIP_BLOCKS
    try:
        conf_file = open(CONFIG_FILE, 'r')
        conf = json.load(conf_file)
        conf_file.close()
        return conf["ranges"]
    except (IOError, ValueError):
        print("""Missing or corrupt {} file. Please use the format:\n"""
              """{\n"""
              """    "ranges":<ranges to retrieve>\n"""
              """}""".format(CONFIG_FILE))
        sys.exit(1)


def write_config(ranges):
    """
    Writes out a config file to save our place between runs.
    """
    conf = {"ranges": ranges}
    conf_file = open(CONFIG_FILE, 'w')
    json.dump(conf, conf_file)
    conf_file.close()


def request_matches(start_id):
    """
    Issues a single request against the Dota API and returns the result as a
    json object. Also responsible for updating the timing information.
    If a bad response is returned sleeps briefly and then tries again.
    """
    global NEXT_REQUEST_TIME, TOTAL_WAIT_TIME, TOTAL_CALLS, TMP
    params = dict(key=API_KEY,
                  start_at_match_seq_num=start_id,
                  matches_requested=MATCHES_PER_REQUEST,
                  skill=3,
                  min_players=10)
    time_to_wait = NEXT_REQUEST_TIME - time.time()
    if time_to_wait > 0:
        # Throttle the requests if necessary, and keep track of wait time.
        time.sleep(time_to_wait)
        TOTAL_WAIT_TIME += time_to_wait
    NEXT_REQUEST_TIME = time.time() + REQUEST_PERIOD
    # stream = False seems to avoid a bug where the request hangs without timing out or returning
    
    url = make_url(start_id)
    resp = requests.get(url, timeout=60 * 2)
    if resp.status_code != requests.codes.ok:
        raise Exception("Bad status code for request: {}".format(resp.status_code))
    TOTAL_CALLS += 1
    return json.loads(resp.content)


def slurp_block(start_seq_id, limit_seq_id, file, cur_seq_id):
    """
    Begins retrieving matches and saves them to an open file. The caller is
    responsible for supplying an open file parameter and closing it.
    Matches will be written to the file one per line.
    start_seq_id: The first seq id number to retrieve. Inclusive.
    limit_seq_id: The seq id number to stop at. Exclusive.
    file: The file to write json match representations to.
    Returns true if there are more matches. Returns false if we get 0 matches,
    which should indicate the end of history.
    """
    if cur_seq_id is not None:
        next_start = cur_seq_id
    else:
        next_start = start_seq_id
    last_logged = next_start
    errors = 0
    while True:
        if(LOG_INTERVAL < next_start - last_logged):
            print("{}: Read up to {} on block {} to {} ({:.3f} percent done)".format
            (datetime.datetime.fromtimestamp(time.time()), next_start, start_seq_id, limit_seq_id, 
            100 * float(next_start - start_seq_id) / float(limit_seq_id - start_seq_id)))
            last_logged = next_start
        try:
            matches = request_matches(next_start)['result']['matches']
        except Exception as e:
            print("Exception caught: ", str(e))
            if(errors > 0):
                print(str(errors + 1), " consecutive errors")
            sleep_time = WAIT_TIMES[min(errors, len(WAIT_TIMES))]
            errors += 1
            print("Sleeping for {} seconds".format(sleep_time))
            time.sleep(sleep_time)
            print("Attempting to continue...")
            continue
        errors = 0
        if not matches:
            return False

        for m in matches:
            if m['match_seq_num'] >= limit_seq_id:
                return True

            # MATCH RULES
            
            # check leavers
            # for j in range(len(m["players"])):
            #     if "leaver_status" in m["players"][j]:
            #         if m["players"][j]["leaver_status"] >=   2:
            #             match_valid = False

            # check match dur > 20 min
            if m["duration"] < 60 * 19:
                continue
            
            # check gamemode 
            if m["game_mode"] not in [1, 2, 22]:
                continue

            json.dump(m, file)
            file.write("\n")
            next_start = m['match_seq_num'] + 1


if __name__ == "__main__":
    # Read in a config file to remember our place, and begin recording.
    ranges = read_config()
    print("Retrieving Dota 2 match history....")
    print("Logging every {} sequence numbers".format(LOG_INTERVAL))
    while True:
        try:
            download_range = ranges.pop(0)
        except IndexError:
            print("Finished with all ranges in config.json.")
            print("Exiting.")
            sys.exit(0)
        print("Downloading range [{},{}).".format(download_range[0], download_range[1]))
        filename = "matches_{}-{}".format(download_range[0], download_range[1])
        tmp_filename = filename + "_INCOMPLETE.json"
        zip_filename = filename + ".gz"
        if os.path.exists(zip_filename):
            print(zip_filename + " already exists!")
            print("Ensure config.json and the files is this " +
                  " directory are consistent and try again")
            exit(-1)

        seq = recover(tmp_filename)
        f = open(tmp_filename, 'a+')
        if not slurp_block(download_range[0], download_range[1], f, seq):
            print("No matches found beyond seq {}".format(download_range[1]))
            print("Exiting.")
            break
        print("Done, zipping the file")
        write_config(ranges)
        f.seek(0, 0)
        gzf = gzip.open(zip_filename, 'wt') ## check this, got error about wanted binary, got str 
        gzf.writelines(f)
        gzf.close()
        f.close()
        os.rename(tmp_filename, "last_incomplete.json")
        # Report some stats.
        print("Total API requests: {}\n"
              "Total wait time: {}\n"
              "Average wait per request: {}".format(TOTAL_CALLS, TOTAL_WAIT_TIME, TOTAL_WAIT_TIME/TOTAL_CALLS))
