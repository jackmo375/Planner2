
class Node:
	def __init__(self, label):
		self.label = label

	# writers:
	def togv(self, out):
		out.write('[label="'+self.label+'"]')

class Record(Node):
	def __init__(self, label, durations, deadlines):
		self.label = label
		self.durations = durations
		self.deadlines = deadlines

	# writers:
	def togv(self, out):
		tab = ' '*4
		out.write(
			' [shape=none, margin=0, label=<'
			+ '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n'
			+ tab + '<TR><TD>'+str(self.durations[0])+'</TD>\t\t// est. duration\n'	# est. duration
			+ tab 	+ '\t<TD>'+str(self.deadlines[0])+'</TD></TR>\t// est. end date\n'	# est. end date
			+ tab + '<TR><TD COLSPAN="2">'+self.label+'</TD></TR>\n'
			+ tab   + '<TR><TD>'+str(self.durations[1])+'</TD>\t\t// est. duration\n'	# est. duration
			+ tab 	+ '\t<TD>'+str(self.deadlines[1])+'</TD></TR>\t// est. end date\n'	# est. end date
			+ tab + '</TABLE>>]')

# readers:
def fromgv(step, inputString):
	if 'edges' in step:
		return Node(inputString.split('"')[1])
	if 'time' in step:
		array = inputString.replace('<','>').split('>')
		label = array[19]
		durations = [float(array[7]), float(array[27])]
		deadlines = [float(array[11]), float(array[31])]
		return Record(label, durations, deadlines)

def fromnode(node):
	return Record(node.label, [1.0,1.0], [1.0,1.0])
