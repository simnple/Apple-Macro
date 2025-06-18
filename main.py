import cv2
import numpy as np
import pyautogui

DEBUG_MODE = False
MOVE_DURATION = 0.2

THRESHOLD = 0.95
FIX_POSITION = 15

X_PIXEL = 17
Y_PIXEL = 10

nums = []

nums_loc = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: []
}

def print_debug(str="", end="\n"):
    if DEBUG_MODE == True: print(str, end=end)

img = pyautogui.screenshot()
img.save('base.png')

base = cv2.imread("./base.png")

for i in range(1, 10):
    num_template = cv2.imread(f"./imgs/{i}.png")

    h, w = num_template.shape[:-1]

    res = cv2.matchTemplate(base, num_template, cv2.TM_CCOEFF_NORMED)

    loc = np.where(res >= THRESHOLD)

    do_continue = False
    for pt in zip(*loc[::-1]):
        for loc in nums_loc[i]:
            if abs(pt[0] - loc["loc1"][0]) < FIX_POSITION and abs(pt[1] - loc["loc1"][1]) < FIX_POSITION:
                print_debug(f"FILTER: {pt}")
                do_continue = True
                break
        
        if do_continue == True:
            do_continue = False
            continue

        print_debug(f"NO_FILTER: {pt} | {i}")
        nums_loc[i].append({"loc1": pt, "loc2": (pt[0] + w, pt[1] + h)})

total = 0
for i in range(1, 10):
    print(f"{i}: {len(nums_loc[i])}")
    total += len(nums_loc[i])

print(f"total: {total}")

x_average = []
y_average = []

for c in range(0, X_PIXEL):
    x_min = []

    for i in range(1, 10):
        for loc in nums_loc[i]:
            do_continue = False
            for x in x_average:
                if abs(loc["loc1"][0] - x) <= (FIX_POSITION/2):
                    do_continue = True
                    break
            
            if do_continue == True: continue
            if len(x_min) == 0:
                x_min.append(loc["loc1"][0])
                continue

            if abs(loc["loc1"][0] - x_min[0]) > FIX_POSITION:
                if x_min[0] > loc["loc1"][0]:
                    x_min = [loc["loc1"][0]]
                    print_debug(f"[X_MIN] [RESET] {loc["loc1"][0]} | {i}")

            else:
                x_min.append(loc["loc1"][0])
                print_debug(f"[X_MIN] [APPEND] {loc["loc1"][0]} | {i}")

    if len(x_min) != Y_PIXEL:
        print_debug("UNEXCEPT ERROR! " * 5)
    print_debug(f"x_min ({len(x_min)}): {sum(x_min)/len(x_min)}")

    x_average.append(sum(x_min)/len(x_min))

for c in range(0, Y_PIXEL):
    y_min = []

    for i in range(1, 10):
        for loc in nums_loc[i]:
            do_continue = False
            for y in y_average:
                if abs(loc["loc1"][1] - y) <= (FIX_POSITION/2):
                    do_continue = True
                    break
            
            if do_continue == True: continue
            if len(y_min) == 0:
                y_min.append(loc["loc1"][1])
                continue

            if abs(loc["loc1"][1] - y_min[0]) > FIX_POSITION:
                if y_min[0] > loc["loc1"][1]:
                    y_min = [loc["loc1"][1]]
                    print_debug(f"[Y_MIN] [RESET] {loc["loc1"][1]} | {i}")

            else:
                y_min.append(loc["loc1"][1])
                print_debug(f"[Y_MIN] [APPEND] {loc["loc1"][1]} | {i}")

    if len(y_min) != X_PIXEL:
        print_debug("UNEXCEPT ERROR! " * 5)
    print_debug(f"y_min ({len(y_min)}): {sum(y_min)/len(y_min)}")

    y_average.append(sum(y_min)/len(y_min))

print_debug(f"x_average ({len(x_average)}): {x_average}")
print_debug(f"y_average ({len(y_average)}): {y_average}")

for y in y_average:
    temps = []
    for x in x_average:
        for i in range(1, 10):
            for loc in nums_loc[i]:
                if abs(loc["loc1"][0] - x) <= (FIX_POSITION/2) and abs(loc["loc1"][1] - y) <= (FIX_POSITION/2):
                    temps.append({"num": i, "loc1": loc["loc1"], "loc2": loc["loc2"]})
    
    nums.append(temps)

print("\n" + "=" * 30)
for i in range(0, Y_PIXEL):
    for j in range(0, X_PIXEL):
        print(f"{nums[i][j]["num"]}", end=" ")
    print()
print("=" * 30)

mouse_queue = []

score = 0

for _ in range(10):
    for i in range(0, Y_PIXEL):
        for j in range(0, X_PIXEL):
            sum = 0
            idx_x = 0
            idx_y = 0

            first_loc = nums[i][j]["loc1"]
            last_loc = nums[i][j]["loc2"]

            while (j + idx_x) < X_PIXEL and (i + idx_y) < Y_PIXEL:
                if nums[i][j]["num"] == 0:
                    break

                if idx_y > 0:
                    for k in range(0, idx_y + 1):
                        sum += nums[i + k][j + idx_x]["num"]

                else:
                    sum += nums[i][j + idx_x]["num"]

                if sum == 10:
                    last_loc = nums[i + idx_y][j + idx_x]["loc2"]
                    print_debug("Pattern: ", end="")
                    for l in range(0, idx_y + 1):
                        for k in range(0, idx_x + 1):
                            if nums[i + l][j + k]["num"] != 0: score += 1
                            print_debug(f"{nums[i + l][j + k]['num']}", end=",")
                            nums[i + l][j + k]["num"] = 0
                    print_debug()
                    print_debug(f"FIND: {first_loc}, {last_loc}")

                    mouse_queue.append({
                        "first_loc": (first_loc[0] - FIX_POSITION, first_loc[1] - FIX_POSITION),
                        "last_loc": (last_loc[0] + FIX_POSITION * 2, last_loc[1] + FIX_POSITION * 2),
                        "duration": MOVE_DURATION + (idx_x * 0.1) + (idx_y * 0.1)
                    })
                    break

                if sum > 10:
                    sum = 0
                    idx_x = 0
                    idx_y += 1

                else:
                    idx_x += 1

    for i in range(0, Y_PIXEL):
        for j in range(X_PIXEL - 1, -1, -1):
            sum = 0
            idx_x = 0
            idx_y = 0

            first_loc = (nums[i][j]["loc2"][0], nums[i][j]["loc1"][1])
            last_loc = (nums[i][j]["loc1"][0], nums[i][j]["loc2"][1])

            while (j + idx_x) > 0 and (i + idx_y) < Y_PIXEL:
                if nums[i][j]["num"] == 0:
                    break

                if idx_y > 0:
                    for k in range(0, idx_y + 1):
                        sum += nums[i + k][j + idx_x]["num"]

                else:
                    sum += nums[i][j + idx_x]["num"]

                if sum == 10:
                    last_loc = (nums[i + idx_y][j + idx_x]["loc1"][0], nums[i + idx_y][j + idx_x]["loc2"][1])
                    print_debug("Pattern: ", end="")
                    for l in range(0, idx_y + 1):
                        for k in range(idx_x, 1):
                            if nums[i + l][j + k]["num"] != 0: score += 1
                            print_debug(f"{nums[i + l][j + k]['num']}", end=",")
                            nums[i + l][j + k]["num"] = 0
                    print_debug()
                    print_debug(f"FIND: {first_loc}, {last_loc}")

                    mouse_queue.append({
                        "first_loc": (first_loc[0] + FIX_POSITION, first_loc[1] - FIX_POSITION),
                        "last_loc": (last_loc[0] - FIX_POSITION * 2, last_loc[1] + FIX_POSITION * 2),
                        "duration": MOVE_DURATION + (-idx_x * 0.1) + (idx_y * 0.1)
                    })
                    break

                if sum > 10:
                    sum = 0
                    idx_x = 0
                    idx_y += 1

                else:
                    idx_x -= 1

print(f"score: {score}")

for mouse in mouse_queue:
    pyautogui.moveTo(mouse["first_loc"][0], mouse["first_loc"][1])
    pyautogui.mouseDown()
    pyautogui.moveTo(mouse["last_loc"][0], mouse["last_loc"][1], mouse["duration"])
    pyautogui.mouseUp()