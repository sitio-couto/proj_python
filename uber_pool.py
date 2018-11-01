from sys import stdin
from numpy import matrix, inf, ones

def build_matrix(data):
    dim = max([max(d[:-1]) for d in data]) + 1
    wmtx = matrix(ones((dim,dim))*inf)
    for i in range(dim): wmtx[i,i] = 0
    for d in data: wmtx[d[0],d[1]] = d[2]
    return wmtx

def floyd_warshall(wmtx):
    print(wmtx)

def read_input( ):
    weight_data = []   # Vertices and weights
    pool_data = []

    line = stdin.readline()[:-1].split(' ') # Processed line
    while (line != ['']):
        weight_data.append([int(line[0]),int(line[1]),float(line[2])])
        line = stdin.readline()[:-1].split(' ')

    line = stdin.readline()[:-1].split(' ')
    while (line != ['']):
        if (len(line) == 3): pool_data.append([int(x) for x in line])
        else: pool_data.append([int(line[0]),-1,int(line[1])])
        line = stdin.readline()[:-1].split(' ')

    return weight_data, pool_data

# MAIN #########################################################################

wd, pd = read_input()

print(wd)
print(pd)

wd = floyd_warshall(build_matrix(wd))

print(wd)
