'''
One of the latest match ids BEFORE patch 7.30e: 6237281052
Use this id to get a list of parsed matches from api.opendota.com.
api_key = 8a0ef958-a013-405a-b419-8c7cbb4e393a
'''

import json
import time
from typing import List
from retrying import retry
import requests

def retry_if_connection_error(exception):
    """ Specify an exception you need. or just True"""
    print("failed, retrying")
    return True
    # return isinstance(exception, ConnectionError)

# if exception retry with 2 second wait  
@retry(retry_on_exception=retry_if_connection_error, wait_fixed=60000)
def safe_request(url, **kwargs):
    return requests.get(url, **kwargs)

if __name__ == "__main__":
    start_match_id = 6237281052
    match_ids = []
    print(f"starting with id {start_match_id}")

    while len(match_ids) < 50000:
        params = {'less_than_match_id': start_match_id}
        try:
            response = safe_request("https://api.opendota.com/api/parsedMatches", params=params) 
            if response.status_code == 429:
                print("too many requests, sleeping for 60 seconds")
                time.sleep(60)
                response = safe_request("https://api.opendota.com/api/parsedMatches", params=params)
        except Exception as e:
            print(e)
        finally:
            parsed_matches = [x["match_id"] for x in response.json()]
            match_ids.extend(parsed_matches)
            start_match_id = match_ids[-1]
            print(f"current match_id: {start_match_id}, len {len(match_ids)}")
    
    print("done, saving to file.")

    # save match_ids to json file
    with open('match_ids.json', 'w') as f:
        json.dump(match_ids, f)

    print("done")





