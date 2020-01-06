import datetime

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
			+ tab + '<TR><TD>'+str(self.durations[0])+'</TD>\t\t// est. duration\n'		# est. duration
			+ tab 	+ '\t<TD>'+str(self.deadlines[0])+'</TD></TR>\t// est. end date\n'	# est. end date
			+ tab + '<TR><TD COLSPAN="2">'+self.label+'</TD></TR>\n'
			+ tab   + '<TR><TD>'+str(self.durations[1])+'</TD>\t\t// est. duration\n'	# est. duration
			+ tab 	+ '\t<TD>'+str(self.deadlines[1])+'</TD></TR>\t// est. end date\n'	# est. end date
			+ tab + '</TABLE>>]')

class GanttNode(Node):
	def __init__(self, label, startDate, deadlines):
		self.label     = label
		self.startDate = startDate
		self.deadlines = deadlines

	# writers:
	def togv(self, out):
		tab = ' '*4
		out.write(
			' [shape=none, margin=0, label=<'
			+ '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\n'
			+ tab + '<TR><TD>'+self.startDate.strftime('%Y-%m-%d')+'</TD></TR>\t\t// est. start date\n'
			+ tab + '<TR><TD COLSPAN="1">'+self.label+'</TD></TR>\n'
			+ tab + '<TR><TD>'+self.deadlines[0].strftime('%Y-%m-%d')+'</TD></TR>\t// schedule deadline\n'
			+ tab + '<TR><TD>'+self.deadlines[1].strftime('%Y-%m-%d')+'</TD></TR>\t// absolute deadline\n'
			+ tab + '</TABLE>>]')

	def togantt(self, out):
		out.write(self.label + ',' + self.startDate.strftime('%Y-%m-%d') + ',' + self.deadlines[0].strftime('%Y-%m-%d') + ',' + self.deadlines[1].strftime('%Y-%m-%d'))


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

def fromNode(node):
	return Record(node.label, [1.0,1.0], [1.0,1.0])

'''
fromRecord()

In this function we assume
that all months are 30 days long. 
Since we are approximating task durations
anyway this is not that important.
'''
def fromRecord(record, unit, firstDay):

	deadlines = []

	if unit == 'month':
		# calculate deadlines from relative values:
		## first deadline:
		nMonths = int(record.deadlines[0])					# number of months from firstDay
		nDays   = int((record.deadlines[0] - nMonths)*30.0)	# approx number of remainder days
		deadlines = deadlines + [firstDay + datetime.timedelta(nMonths*30 + nDays)]
		## second deadline:
		nMonths = int(record.deadlines[1])					# number of months from firstDay
		nDays   = int((record.deadlines[1] - nMonths)*30.0)	# approx number of remainder days
		deadlines = deadlines + [firstDay + datetime.timedelta(nMonths*30 + nDays)]
		## start date:
		nMonths = int(record.durations[0])					# number of months of first duration
		nDays   = int((record.durations[0] - nMonths)*30.0)	# approx number of remainder days
		startDate = deadlines[0] + datetime.timedelta(-nMonths*30 - nDays)
	else:
		print('units are not months')

	return GanttNode(record.label, startDate, deadlines)
