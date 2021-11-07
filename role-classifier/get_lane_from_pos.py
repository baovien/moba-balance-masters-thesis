import json

lane_mappings = []
for i in range(0, 128):
    lane_mappings.append([])
    for j in range(0, 128):
        lane = 0
        if abs(i - (127 - j)) < 8:
            lane = 2 # mid
        elif j < 27 or i < 27:
            lane = 3 # top
        elif j >= 100 or i >= 100:
            lane = 1 # bot
        elif i < 50:
            lane = 5 # djung
        elif i >= 77:
            lane = 4 # rjung
        else:
            lane = 2 # mid
    
        lane_mappings[i].append(lane)

#  Finds the mode and its occurrence count in the input array. return mode and count
def mode(array):
    # initialize mode and count
    mode = 0
    count = 0
    # iterate over the input array
    for i in array:
        # if the count is 0, set the mode to the current element
        if count == 0:
            mode = i
        # if the current element is equal to the mode, increment the count
        if i == mode:
            count += 1
        # if the current element is not equal to the mode, then the count is 0
        else:
            count = 0
    return mode, count


def mode_with_count(arr):
    if not len(arr):
        return {}
    
    mode_map = {}
    max_el = arr[0]
    max_count = 1
    for el in arr:
        if mode_map[el] is None:
            mode_map[el] = 1
        else:
            mode_map[el] += 1
        
        if mode_map[el] > max_count:
            max_count = mode_map[el]
            max_el = el

    return max_el, max_count

def is_radiant(player):
    return player.player_slot < 128

def get_lane_from_post_data(lane_pos, is_radiant):
    # compute lanes
    lanes = []

    # iterate over the position hash and get the lane bucket for each data point
    for x in lane_pos:
        for y in lane_pos[x]:
            val = lane_pos[x][y]
            adjX = int(x) - 64
            adjY = 128 - (int(y) - 64)
            # add it N times to the array
            for _ in range(val):
                if lane_mappings[adjY] and lane_mappings[adjY][adjX]:
                    lanes.append(lane_mappings[adjY][adjX])


    lane, count = mode_with_count(lanes)
    is_roaming = (count/len(lanes)) < 0.45
    lane_roles = {
        1: 1 if is_radiant else 3, #bot
        2: 2,                      #mid
        3: 3 if is_radiant else 1, #top
        4: 4,                      #radiant jungle
        5: 4                       #dire jungle
    }

    return {"lane": lane, "lane_role": lane_roles[lane], "is_roaming": is_roaming }



if __name__ == "__main__":
    with open("data/example.json") as f:
        match = json.load(f)

    print(match["players"][0])