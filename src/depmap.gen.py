import sys, network

def main():

	label = sys.argv[1]
	step = '.edges'
	print(label+'.csv')

	a = network.fromcsv(label)

	a.togv(label, step)


if __name__ == '__main__':
	main()