import random


maps = [
    [0,1],
    [3,13,23],
    [20,30,40,50],
    [70,71],
    [56,66],
    [6,7,8,9],
    [25,26,27],
    [29,39],
    [59,69,79],
    [95,96,97,98,99],
    [53,63,73],
    [91,92]
]

def gen_map(maps):
    map_list =[]
    indexes = []
    while indexes.__len__() <5:
        i = random.randint(0,11)
        if i not in indexes:
            indexes.append(i)
    for j in indexes:
        map_list+=maps[j]
    return map_list

if __name__ == "__main__":
    gen_map(maps)
