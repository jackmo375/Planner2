import tasks, node

class Network:
	def __init__(self, nodes, edges):
		self.nodes = nodes
		self.edges = edges
		self.cPath = []

	def updateDeadlines(self):
		if self.nodes[0].__class__.__name__ != 'Record':
			raise Exception('Network Error: can only update deadlines for records')
		L = self.topSort()
		# update 1st deadlines
		durations = []
		for n in self.nodes:
			durations = durations + [n.durations[0]]
		deadlines = cumulativeTime(durations, L, range(len(self.nodes)), self.edges)
		i = 0
		for n in self.nodes:
			n.deadlines[0] = deadlines[i]
			i += 1

		# update 2nd deadlines
		durations = []
		for n in self.nodes:
			durations = durations + [n.durations[1]]
		deadlines = cumulativeTime(durations, L, range(len(self.nodes)), self.edges)
		i = 0
		for n in self.nodes:
			n.deadlines[1] = deadlines[i]
			i += 1

	def criticalPath(self):
		
		deadlines = []
		for n in self.nodes:
			deadlines = deadlines + [n.deadlines[0]]
		self.cPath = criticalPath(range(len(self.nodes)), self.edges, deadlines)


	def topSort(self):
		V = range(len(self.nodes))
		return topSort(V, self.edges)

	# Writers:
	def togv(self, label, step):
		outstream = open(label+step+'.gv', 'w')
		self._beginGraph(outstream, label)
		outstream.write('/* Nodes */\n')
		i = 0
		for n in self.nodes:
			outstream.write(' '*4 + str(i) + ' ')
			n.togv(outstream)
			outstream.write(';\n')
			i += 1
		outstream.write('/* Edges */\n')
		if self.cPath == []:
			for e in self.edges:
				outstream.write(' '*4 + str(e[0])+' -> '+str(e[1])+'\n')
		else:
			for e in self.edges:
				if not e in self.cPath:
					outstream.write(' '*4 + str(e[0])+' -> '+str(e[1])+'\n')
			outstream.write('/* Critical path */\n')
			outstream.write('edge [color=red];\n')
			for e in self.cPath:
				outstream.write(' '*4 + str(e[0])+' -> '+str(e[1])+'\n')
		outstream.write('}')
		outstream.close()

	# Private members
	def _beginGraph(self, out, graphName):
		out.write("digraph "+graphName+" {\n")


# Readers:
def fromcsv(label):

	return fromTaskList(tasks.TaskList(label+'.csv'))


def fromTaskList(tasklist):

	nodes = []
	for task in tasklist.tasks:
		nodes = nodes + [node.Node(task[tasklist.maxIndent])]

	edges = []
	for i in range(len(nodes)-1):
		edges = edges + [[i,i+1]]

	return Network(nodes, edges)

def fromgv(label, step):

	nodes = []
	edges = []

	instream = open(label+step+'.gv', 'r', encoding='utf-8-sig')
	fileSection = '0'
	j = 0	# task index

	while True:

		line = instream.readline()
		if not line:
			break

		# skip blank lines:
		if line.strip() == '':
			continue

		# get task names and durations:
		if '/* Nodes */' in line.strip():
			fileSection = 'nodes'
			continue
		elif '/* Edges */' in line.strip():
			fileSection = 'edges'
			continue
		elif '/* Ranks */' in line.strip():
			fileSection = 'ranks'
			continue
		elif '/* Critical path */' in line.strip() or 'edge [color=red];' in line.strip():
			continue
		elif fileSection != 'nodes' and '}' in line.strip():
			continue
		else:
			pass

		# get task info
		if fileSection == 'nodes':
			nodeString = ''
			while True:
				nodeString = nodeString + line
				if ';' in line:
					break
				line = instream.readline()
			nodes = nodes + [node.fromgv(step, nodeString)]

		# get dependency info
		if fileSection == 'edges':
			if not ',' in line:
				array = line.strip().split("->")
				edges = edges + [[int(array[0]), int(array[1])]]
			else:
				array = line.strip().split("->")
				if ',' in array[0]:
					edges = edges + [[int(array[0].split(',')[0]), int(array[1])]]
					edges = edges + [[int(array[0].split(',')[1]), int(array[1])]]
				else:
					edges = edges + [[int(array[0]), int(array[1].split(',')[0])]]
					edges = edges + [[int(array[0]), int(array[1].split(',')[1])]]



	instream.close()

	return Network(nodes, edges)


# graph algorithms
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

def criticalPath(nodes, edges, deadlines):

	S  = [] # node sequence
	CP = []	# critical path edge set

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