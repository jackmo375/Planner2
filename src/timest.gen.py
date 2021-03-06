import sys, network, node

def main():

	label = sys.argv[1]
	step = '.time'
	prevStep = '.edges' 

	# read network diagram from previous step:
	a = network.fromgv(label, prevStep)

	# convert from nodes to records:
	b = network.Network([], a.edges)
	for n in a.nodes:
		b.nodes = b.nodes + [node.fromNode(n)]

	# update deadlines:
	b.updateDeadlines()
	# update critical path:
	b.criticalPath()

	# print updated network diagram:
	b.togv(label, step)

if __name__ == '__main__':
	main()