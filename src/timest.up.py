import sys, network, node

def main():

	label = sys.argv[1]
	step = '.time'

	b = network.fromgv(label, step)

	# update deadlines:
	b.updateDeadlines()
	# update critical path:
	b.criticalPath()

	b.togv(label,step)

if __name__ == '__main__':
	main()