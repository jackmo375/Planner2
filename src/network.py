#
#	Network Diagram class
#

import tasks, node, graph

class Network:
	def __init__(self, nodes, edges, cPath=[]):
		self.nodes = nodes
		self.edges = edges
		self.cPath = cPath

	def updateDeadlines(self):
		if self.nodes[0].__class__.__name__ != 'Record':
			raise Exception('Network Error: can only update deadlines for records')
		L = self.topSort()
		# update 1st deadlines
		durations = []
		for n in self.nodes:
			durations = durations + [n.durations[0]]
		deadlines = graph.cumulativeTime(durations, L, range(len(self.nodes)), self.edges)
		i = 0
		for n in self.nodes:
			n.deadlines[0] = deadlines[i]
			i += 1

		# update 2nd deadlines
		durations = []
		for n in self.nodes:
			durations = durations + [n.durations[1]]
		deadlines = graph.cumulativeTime(durations, L, range(len(self.nodes)), self.edges)
		i = 0
		for n in self.nodes:
			n.deadlines[1] = deadlines[i]
			i += 1

	def criticalPath(self):
		
		deadlines = []
		for n in self.nodes:
			deadlines = deadlines + [n.deadlines[0]]
		self.cPath = graph.longestPath(range(len(self.nodes)), self.edges, deadlines)


	def topSort(self):
		V = range(len(self.nodes))
		return graph.topSort(V, self.edges)

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

	def togantt(self, label, step):
		# check the nodes are Gantt nodes:
		if self.nodes[0].__class__.__name__ != 'GanttNode':
			raise Exception('Network Error: can only print Gantt charts for Gantt nodes')

		outstream = open(label+step+'.txt', 'w')
		for n in self.nodes:
			n.togantt(outstream)
			outstream.write('\n')
		outstream.close()

	def toical(self, label, step):
		if self.nodes[0].__class__.__name__ != 'GanttNode':
			raise Exception('Network Error: can only print calendars for Gantt nodes')

		outstream = open(label+step+'.ical', 'w')
		self._beginCalendar(label, outstream)
		for n in self.nodes:
			n.toical(outstream)
		self._endCalendar(outstream)

		outstream.close()


	# Private members
	def _beginGraph(self, out, graphName):
		out.write("digraph "+graphName+" {\n")

	def _beginCalendar(self, label, out):
		out.write(
			'BEGIN:VCALENDAR\n'
			+ 'PRODID:-//K Desktop Environment//NONSGML libkcal 4.3//EN\n'
			+ 'VERSION:2.0\n'
			+ 'X-KDE-ICAL-IMPLEMENTATION-VERSION:1.0\n'
			+ 'X-WR-CALNAME:'+label+'\n'
			+ 'X-WR-TIMEZONE:Africa/Johannesburg\n'
		)
	def _endCalendar(self, out):
		out.write(
			'END:VCALENDAR'
		)


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
