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

class Rider():
    def __init__(self, id, data):
        self.id = id                  # passenger id
        self.s, self.c, self.f = data # start, current and finishing vertices
    def __str__(self):
        return str([self.id, self.s, self.c, self.f])

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

    return wmtx, pmtx, dim                     #Returns weigths, parents and dimension

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
    id = 0             # Passenger ID
    weight_data = []   # Vertices and weights
    pool_data = []     # Passengers path data

    line = stdin.readline()[:-1].split(' ') # Processed line
    while (line != ['']):                   # Read first chunk of text (weights)
        weight_data.append([int(line[0]),int(line[1]),float(line[2])])
        line = stdin.readline()[:-1].split(' ')

    line = stdin.readline()[:-1].split(' ')
    while (line != ['']):                   # Read second chunck of text (paths)
        if (len(line) == 3): pool_data.append(Rider(id,[int(x) for x in line]))
        else: pool_data.append(Rider(id,[int(line[0]),-1,int(line[1])]))
        line = stdin.readline()[:-1].split(' ')
        id += 1

    return weight_data, pool_data

def pool_order(p1, p2, w):
    pool_times = []

    # Times without pooling
    p1_t = w[p1.s,p1.f]
    p2_t = w[p2.s,p2.f]
    #pick P1 first, drop P1 last
    pool_times.append(['A', w[p1.s,p2.s]+w[p2.s,p2.f]+w[p2.f,p1.f], w[p2.s,p2.f]])
    #pick P1 last, drop P1 last
    pool_times.append(['B', w[p1.s,p2.f]+w[p2.f,p1.f], w[p2.s,p1.s]+w[p1.s,p2.f]])
    #pick P1 first, drop P1 first
    pool_times.append(['C', w[p1.s,p2.s]+w[p2.s,p1.f], w[p2.s,p1.f]+w[p1.f,p2.f]])
    #pick last, drop first
    pool_times.append(['D', w[p1.s,p1.f], w[p2.s,p1.s]+w[p1.s,p1.f]+w[p1.f,p2.f]])

    best = min(pool_times, key=lambda x: max([x[1]/p1_t, x[2]/p2_t]))
    return best[0], max([best[1]/p1_t, best[2]/p2_t])

def pool_order_ongoing(og, ra, w):
    pool_times = []

    # Times without pooling
    og_t = w[og.c,og.f] # From current node to finish
    ra_t = w[ra.s,ra.f]
    # Drop og first
    pool_times.append(['F', w[og.c,ra.s]+w[ra.s,og.f], w[ra.s,og.f]+w[og.f,ra.f]])
    # Drop og last
    pool_times.append(['E', w[og.c,ra.s]+w[ra.s,ra.f]+w[ra.f,og.f], w[ra.s,ra.f]])

    best = min(pool_times, key=lambda x: max([x[1]/og_t, x[2]/ra_t]))
    return best[0], max([best[1]/og_t, best[2]/ra_t])

def incovenience(p1, p2, wm)
    if p1. < 0 : # If p1 is ongoing
        pool_order('p1',p1,p2,wm)

         min([wm[p1.mid,p2.start]+wm[p2.start,]/wm[]]) # Drop P2 after P1
        return
    elif p2[1] < 0 : # If p2 is ongoing
        incovenience()
    else: # If none are ongoing
        incovenience()

def combine_passengers(result, paths, weights):
    if(len(paths) == 1):
        return result
    else:
        p1 = paths.pop()
        for p2 in paths:
            # Add p1 traveling alone in case theres no pair available/possible
            result.append([p1.id, -1, inf])
            # If both passenger are already traveling, do not combine
            if p1[2]*p2[2] > 0 : continue
            # If inconvenience > 1.4, do not combine
            incv = incovenience(p1, p2, weights)
            if incv <= 1.4: result.append([p1.id,p2.id,incv])

    return

# MAIN #########################################################################

weights, paths = read_input()
print(read_input.calls)
print("Riders data:")
for x in paths: print(x)

weights, parents, dim = build_matrix(weights)
print(build_matrix.calls)

weights, parents = floyd_warshall(weights, parents, dim)
print(floyd_warshall.calls)

# combine_passengers()

# NOTAS:
# 1 - A inconveniência para um passageiro por estar dividindo a viagem é a
# razão do tempo da viagem com carona pelo tempo da viagem sem carona.
# 2 - A uber minimiza o máximo da inconveniência para os 2 passageiros.
# 3 - Inconveniência máxima para um passageiro é 1.4, ou seja, usando a carona,
# nunca voce terá um acréscimo maior que 40% no tempo de viagem.
# 4 - Escolhe o percurso de menor inconveniência máxima no caso de mutiplas
# possibilidades.
# 5 - No máximo 2 passageiros farão uma viagem compartilhada.
# 6 - Viagens em anadamento:
#     - Dois passageiros com viagem em anadamento nao compartilham carona.
#     - Para o passageiro 1 a inconveniencia deve ser calculada usando o tempo
#       restante da viagem e não o tempo total.
#     - Ela ja começou em A, (esta agora em X) e portanto os únicos 2 percursos
#       possíveis são A,X,C,B,D ou A,X,C,D,B (limita percurso possivel para saida).
