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
    id = 1             # Passenger ID
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

# This function is responsoble for calculating the inconvenience of all possible
# paths permutations (EX: pick P1, pick P2, drop P2 and then drop P1).
# It also finds the least inconvenient path by minimizing the maximum inconvenience
# of each pair of passengers.
# Arguments:
#   p1 - Passenger (Rider class instance)
#   p2 - Paired passenger (Rider class instance)
#   w  - Cost of each path
# Return:
#   best[0]  - Path permutation used
#   max(...) - Max inconvenience of the passengers for the most convenient path
def pool_order(p1, p2, w):
    pool_times = []

    # Times without pooling
    p1_t = w[p1.s,p1.f]
    p2_t = w[p2.s,p2.f]
    if (p1_t == inf or p2_t == inf): return [-1,inf] # If no path, return invalid

    #pick P1 first, drop P1 last
    pool_times.append(['A', w[p1.s,p2.s]+w[p2.s,p2.f]+w[p2.f,p1.f], w[p2.s,p2.f]])
    #pick P1 last, drop P1 last
    pool_times.append(['B', w[p1.s,p2.f]+w[p2.f,p1.f], w[p2.s,p1.s]+w[p1.s,p2.f]])
    #pick P1 first, drop P1 first
    pool_times.append(['C', w[p1.s,p2.s]+w[p2.s,p1.f], w[p2.s,p1.f]+w[p1.f,p2.f]])
    #pick P1 last, drop P1 first
    pool_times.append(['D', w[p1.s,p1.f], w[p2.s,p1.s]+w[p1.s,p1.f]+w[p1.f,p2.f]])

    # Remove infinity wait from pools possibilities
    pool_times = [p for p in pool_times if p[1]!=inf and p[2]!=inf]
    if pool_times == [] : return [-1,inf] # If no pool possible,return invalid

    best = min(pool_times, key=lambda x: max([x[1]/p1_t, x[2]/p2_t]))
    return get_order(best[0], p1, p2), max([best[1]/p1_t, best[2]/p2_t])

# This function is responsible for calculating the inconvenience of all possible
# paths permutations, considering one passenger is already travelling.
# It also finds the least inconvenient path by minimizing the maximum inconvenience
# of each pair of passengers.
# Arguments:
#   og - Ongoing passenger (already travelling)
#   ra - Ride along passenger (possible lift)
#   w  - Cost of each path
# Return:
#   best[0]  - Path permutation used
#   max(...) - Max inconvenience of the passengers for the most convenient path
def pool_order_ongoing(og, ra, w):
    pool_times = []

    # Times without pooling
    og_t = w[og.c,og.f] # From current node to finish
    ra_t = w[ra.s,ra.f]
    if (og_t == inf or ra_t == inf): return [-1,inf] # If no path, return empty

    # Drop og last
    pool_times.append(['E', w[og.c,ra.s]+w[ra.s,ra.f]+w[ra.f,og.f], w[ra.s,ra.f]])
    # Drop og first
    pool_times.append(['F', w[og.c,ra.s]+w[ra.s,og.f], w[ra.s,og.f]+w[og.f,ra.f]])

    # Remove infinity wait from pools possibilities
    pool_times = [p for p in pool_times if p[1]!=inf and p[2]!=inf]
    if pool_times == [] : return [-1,inf] # If no pool possible,return invalid

    best = min(pool_times, key=lambda x: max([x[1]/og_t, x[2]/ra_t]))
    return get_order(best[0], og, ra), max([best[1]/og_t, best[2]/ra_t])


# This function combines all passengers with all others, returning all the
# valid lifts (considering the inconvenience and possible permutations of
# the path used for the travel).
# Arguments:
#   paths   - origin and destination of each passenger
#   weights - best path or all vertices to all vertices
#   result  - possible combinarions of passengers
# Return - possible combinarions of passengers
def combine_lifts(paths, weights, result=[]):
    if(paths == []): return result       # Recursion base case
    p1 = paths.pop(0)                    # Remove p1 from list

    if p1.c < 0 : result.append([p1.id, -1, [p1.s,p1.f], inf]) # Add p1 traveling alone
    else : result.append([p1.id, -1, [p1.c,p1.f], inf])        # Add p1 traveling alone and ongoing

    for p2 in paths:
        if p1.c >= 0 and p2.c >= 0 : # If both are already traveling, skip
            continue
        elif p1.c >= 0 :   # If only p1 is ongoing
            order, incv = pool_order_ongoing(p1,p2,weights)
        elif p2.c >= 0 :   # If only p2 is ongoing
            order, incv = pool_order_ongoing(p2,p1,weights)
        else:              # If none are ongoing
            order, incv = pool_order(p1, p2, weights)

        if incv <= 1.4:    # If inconvenience > 1.4, do not add
            result.append([p1.id, p2.id, order, incv])

    return combine_lifts(paths, weights, result)

# This function reduces the amount of combinations calculated by selecting the
# the most convenient pair of passengers and path, and removing any remaining
# combination associated to them (EX: any other path containing A and B should
# be removed from comb).
# Arguments:
#   comb - Passengers combination sorted by inconvenience (ascending from top-bottom)
# Return - Less inconvenient set of trips containing all passengers
def reduce(comb, result=[]):
    if comb == []: return result # Recursion base case
    # Takes first element from combinations
    aux = comb.pop(0)
    result.append(aux)
    p1 = aux[0]
    p2 = aux[1]
    # Removes any combination with the same passenger
    if p1 > -1 : comb = [x for x in comb if x[0] != p1]
    if p2 > -1 : comb = [x for x in comb if x[1] != p2]

    return reduce(comb, result)

# This function translates the paths permutation into a array wich represents
# each stop (pick or drop) in the optimal order.
# Arguments:
# type - Char wich indicates the order of picks and drops
# p1   - passenger data (Rider class)
# p2   - passenger data (Rider class)
# Return - Array with vertices in the permutation order
def get_order(type, p1, p2):
    return {
        'A':[p1.s,p2.s,p2.f,p1.f],
        'B':[p2.s,p1.s,p2.f,p1.f],
        'C':[p1.s,p2.s,p1.f,p2.f],
        'D':[p2.s,p1.s,p1.f,p2.f],
        'E':[p1.c,p2.s,p2.f,p1.f],
        'F':[p1.c,p2.s,p1.f,p2.f],
    }.get(type)

def print_output(comb, wm, pm):

    while comb != [] :
        data = comb.pop(0)
        if data[1] == -1 : print("Passenger ", data[0], " alone")
        else : print("Passenger ", data[0], " and ", data[1])
        path, cost = backtrack(data[2], wm, pm)
        print("Path:", path, "\nCost: ", cost)

def backtrack(nodes, wm, pm):
    print(nodes)
    cost = 0
    i = nodes.pop()
    path = str(i)
    while nodes != [] :
        end = i
        i = nodes.pop()
        while i != end :
            path = str(int(pm[i,end])) + " " + path
            cost += wm[i,end]
            end = int(pm[i,end])

    return path, cost
# MAIN #########################################################################

weights, paths = read_input()
# print(read_input.calls)
# print("Riders data:")
# for x in paths: print(x)

weights, parents, dim = build_matrix(weights)
# print(build_matrix.calls)

weights, parents = floyd_warshall(weights, parents, dim)
print(floyd_warshall.calls)

combinations = sorted(combine_lifts(paths.copy(), weights), key=lambda x: x[3])
combinations = reduce(combinations)

print_output(combinations, weights, parents)

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
