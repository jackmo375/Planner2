import sys, network, datetime, node

def main():
	label    = sys.argv[1]
	step     = '.gantt'
	prevStep = '.time'

	unit = 'month'

	# chose the date work is due to start on:
	firstDay = datetime.date(2020, 2, 1)

	# read network diagram from previous step:
	a = network.fromgv(label, prevStep)
	a.criticalPath()

	# convert records to gantt nodes:
	b = network.Network([], a.edges, a.cPath)
	for n in a.nodes:
		b.nodes = b.nodes + [node.fromRecord(n, unit, firstDay)]

	# print...
	# ...final network diagram:
	b.togv(label, step)

	# ...gantt chart:
	b.togantt(label, step)

	# ...google calendar:
	b.toical(label, step)

if __name__ == '__main__':
	main()