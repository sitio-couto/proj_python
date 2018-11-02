from sys import stdin
from numpy import matrix, inf, ones

class return_decorator():
    def __init__(self, f):
        self.f = f
        self.calls = "\n"
    def __call__(self, *args):
        ret = self.f(*args)
        self.calls += "Function: "+self.f.__name__+"\nReturn:\n"
        for r in enumerate(ret): self.calls += str(r[1])+"\n"
        return ret

@return_decorator
def build_matrix(data):
    dim = max([max(d[:-1]) for d in data]) + 1 #Get matrix dimension
    pmtx = matrix(ones((dim,dim))*inf)         #Initialize parents with inf
    wmtx = matrix(ones((dim,dim))*inf)         #Initialize weights with inf
    for i in range(dim):
        pmtx[i,i] = i                          #Set parent to self
        wmtx[i,i] = 0                          #Set diagonal to 0


    for d in data:                             #Adds weights and parents from data
        wmtx[d[0],d[1]] = d[2]
        pmtx[d[0],d[1]] = d[0]

    return wmtx, pmtx, dim                     #Returns weigths, parents and dimensions

@return_decorator
def floyd_warshall(w, p, dim):
    for k in range(dim):
        for i in range(dim):
            for j in range(dim):
                if (w[i,k]+w[k,j] < w[i,j]):
                    w[i,j] = w[i,k]+w[k,j]
                    p[i,j] = p[k,j]

    return w, p

@return_decorator
def read_input( ):
    weight_data = []   # Vertices and weights
    pool_data = []     # Passengers path data

    line = stdin.readline()[:-1].split(' ') # Processed line
    while (line != ['']):                   # Read first chunk of text (weights)
        weight_data.append([int(line[0]),int(line[1]),float(line[2])])
        line = stdin.readline()[:-1].split(' ')

    line = stdin.readline()[:-1].split(' ')
    while (line != ['']):                   # Read second chunck of text (paths)
        if (len(line) == 3): pool_data.append([int(x) for x in line])
        else: pool_data.append([int(line[0]),-1,int(line[1])])
        line = stdin.readline()[:-1].split(' ')

    return weight_data, pool_data

# MAIN #########################################################################

weights, paths = read_input()
print(read_input.calls)

weights, parents, dim = build_matrix(weights)
print(build_matrix.calls)

weights, parents = floyd_warshall(weights, parents, dim)
print(floyd_warshall.calls)
