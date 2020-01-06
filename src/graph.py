# 
# Graph Algorithms
#

def parentsOf(vert, edges):
	 P = []

	 for edge in edges:
	 	if vert == edge[1]:
		 	P = P + [edge[0]]

	 return P

def childrenOf(vert, edges):
	C = []

	for edge in edges:
		if  vert == edge[0]:
			C = C + [edge[1]]

	return C

# topological sorting
def topSort(verts, edges):

	# create copy of edges set:
	edgesCopy = edges.copy()

	L = []

	S = []
	for v in verts:
		if parentsOf(v, edgesCopy) == []:
			S = S + [v]

	# Khan's algorithm
	while S != []:
		L = L + [S.pop(0)]
		for m in childrenOf(L[-1], edgesCopy):
			edgesCopy.remove([L[-1],m])
			if parentsOf(m, edgesCopy) == []:
				S = S + [m]

	if edgesCopy != []:
		raise Exception('graph has at least one cycle')
	else:
		return L

def cumulativeTime(Dur, L, nodes, edges):

	result = [0]*len(Dur)

	for l in L:
		i = nodes.index(l)
		if parentsOf(nodes[i], edges) == []:
			result[i] = Dur[i]
		else:
			max = 0
			for n in parentsOf(nodes[i], edges):
				j = nodes.index(n)
				if result[j] > max:
					max = result[j]
			result[i] = max + Dur[i]

	return result

'''
longestPath:

Computes longest path from node (not edge) weights
'''
def longestPath(nodes, edges, deadlines):

	S  = [] # node sequence
	CP = []	# longest path edge set

	# find endpoint
	max = 0
	indexEnd = 0
	for i in range(len(nodes)):
		if childrenOf(nodes[i], edges) == [] and deadlines[i] > max:
			max = deadlines[i]
			indexEnd = i
	S = S + [nodes[indexEnd]]

	# find node sequence
	indexPrevious = 0
	while parentsOf(S[0], edges) != []:
		max = 0
		for n in parentsOf(S[0], edges):
			j = nodes.index(n)
			if deadlines[j] > max:
				max = deadlines[j]
				indexPrevious = j
		S = [indexPrevious] + S

	# move edges from the edge set to CP
	for i in range(len(S)-1):
		CP = CP + [[S[i],S[i+1]]]

	return CP