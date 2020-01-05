#
#	Task List python module
#
#############################
import sys, csv

class TaskList:
	
	def __init__(self, infile, status='todo', subgraph='t'):
		if status != 'todo' and status != 'all':
			raise ValueError('please chose status as either: todo or all')
			exit(1)
		if subgraph.lower() != 't' and subgraph.lower() != 'f':
			raise ValueError('please chose true (t) or false (f) for subgraph parameter')
			exit(1)
		if subgraph=='t':
			self.subgraphing = True
		else:
			self.subgraphing = False
		instream = open(infile, "r", encoding='utf-8-sig')
		self.infile  = infile
		self.headers = instream.readline().strip().split(",")
		self.maxIndent = self.getMaxIndent()
		self.headerDict = {self.headers[i]:i for i in range(len(self.headers))}
		self.tasks   = []

		for line in csv.reader(instream):
			if len(line) <= 3:
				continue
			# if requested, keep only incomplete tasks/items:
			if line[self.headerDict['Status']]!='To-Do' and status=='todo':
				continue
			self.tasks = self.tasks + [line]

		self.Nnodes     = 0	# private
		self.Nsubgraphs = 0 # private
		self.tb = '    '
		instream.close()

	def printGraph(self):
		self.beginGraph("G")
		print("/* Nodes */")
		self.printGraphNodes()
		print("/* Edges */")
		self.printGraphEdges()
		print("/* Ranks */")
		self.endGraph(-1)

	def printGraphNodes(self, asrecords=False):
		if asrecords == False:
			printX = self.printNode
		else:
			printX = self.printRecord
		i = 0	# index for task list
		j = 0	# index for graph nodes
		k = 0	# index for subgraphs
		while i < len(self.tasks)-1:
			il = self.getIndentLevel(i)
			il_next = self.getIndentLevel(i+1)
			if il<il_next:
				self.beginSubgraph(i,k)
				k+=1
			elif il==il_next:
				printX(i,j)
				j+=1
			else:
				printX(i,j)
				while il>il_next:
					self.endSubgraph(il-1)
					il -= 1
				j+=1
			i+=1
		printX(i,j)
		j+=1
		self.Nnodes     = j
		self.Nsubgraphs = k
		# print any remaining "}"s needed to close the graphs:
		while il >= 1:
			self.endSubgraph(il-1)
			il-=1

	def printGraphEdges(self):
		for i in range(self.Nnodes-1):
			print(self.tb+str(i)+' -> '+str(i+1))

	def getMaxIndent(self):
		i=1
		while(self.headers[i]=='"ID"'):
			i+=1
		return i

	def getIndentLevel(self, taskindex):
		for i in range(self.maxIndent):
			if self.tasks[taskindex][i]!='':
				return i

	def getDueDate(self,taskindex):
		return self.tasks[taskindex][self.maxIndent+6]

	def beginGraph(self,label):
		print("digraph "+label+" {")

	def beginSubgraph(self,taskindex,subindex):
		if self.subgraphing:
			print(
				self.tb*(self.getIndentLevel(taskindex)+1)
				+ 'subgraph cluster_'
				+ str(subindex)
				+ ' {'
			)
			print(
				self.tb*(self.getIndentLevel(taskindex)+2)
				+ 'label="'
				+ self.tasks[taskindex][self.maxIndent]
				+ '";'
			)
		else:
			print(
				self.tb*(self.getIndentLevel(taskindex)+2)
				+ "/* "
				+ self.tasks[taskindex][self.maxIndent]
				+ ": */"
			)

	def endSubgraph(self,indent):
		if self.subgraphing:
			self.endGraph(indent)
		else:
			pass

	def endGraph(self,indent):
		print(self.tb*(indent+1)+"}")

	def printNode(self, taskindex, nodeindex):
		if self.tasks[taskindex][self.maxIndent+10].find('$w')==-1:
			self.printTaskNode(taskindex,nodeindex)
		else:
			self.printWaitNode(taskindex,nodeindex)

	def printTaskNode(self,taskindex,nodeindex):
		print(
			self.tb*(self.getIndentLevel(taskindex)+1)
			+ str(nodeindex) 
			+ ' [label="'
			+ self.tasks[taskindex][self.maxIndent]
			+ '"];'
			)
	def printWaitNode(self,taskindex,nodeindex):
		print(
			self.tb*(self.getIndentLevel(taskindex)+1)
			+ str(nodeindex) 
			+ ' [label="'
			+ self.tasks[taskindex][self.maxIndent]
			+ '",shape=box];'
		)

	def printRecord(self, taskindex, nodeindex):
		taskcomment = self.tasks[taskindex][self.maxIndent+10]
		posw = taskcomment.find('$w')
		post = taskcomment.find('$t')
		duration = ''
		if posw != -1 and post == -1:
			duration = taskcomment[posw:taskcomment[posw:-1].find(']')][3:]
		elif post != -1 and posw == -1:
			duration = taskcomment[post:taskcomment[post:-1].find(']')][3:]
		elif post == -1 and posw == -1:
			duration = '1'	# default value
		else:
			raise ValueError('block can\'t be both task and wait.')
		tab=self.tb*(self.getIndentLevel(taskindex)+1)
		print(
			tab
			+ str(nodeindex) 
			+' [shape=none, margin=0, label=<'
			+ '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n'
			+ tab + '<TR><TD COLSPAN="2">'+self.tasks[taskindex][self.maxIndent]+'</TD></TR>\n'
			+ tab + '<TR><TD>'+duration+'</TD>\t// est. duration\n'	# est. duration
			+ tab 	+ '\t<TD>'+self.getDueDate(taskindex)+'</TD>\t// est. end date\n'	# est. end date
			+ tab + '</TR></TABLE>>];\n'
		)