import time, json, sys

int_type = type(1)

def generateTree(filename):
    lines = open(filename).read().split('\n')
    tree = {}

    j = 0

    for line in lines:
        if line == '':
            continue
        try:
            _,_,size,_,_,path = line.split(maxsplit=5)
            size = int(size)
            path = path.split('/')
            node = tree
            for i in range(len(path)-1):
                try:
                    node = node[path[i]]
                except KeyError:
                    node[path[i]] = {}
                    node = node[path[i]]
            if path[-1]:
                node[path[-1]] = size
        except:
            print(j, line, line.split(maxsplit=5))
            break

        if j % 1000 == 0:
            print(j)
        j += 1

    json.dump(tree, open('tree.json', 'w'))

def recurse(indict, jsonstruct):
    for key in indict:
        try:
            if type(indict[key]) == int_type:
                jsonstruct.append({'name': key, 'asize': indict[key], 'dsize': indict[key]})
            else:
                jsonstruct.append([{'name': key}])
                recurse(indict[key], jsonstruct[-1])
        except SystemExit:
            raise SystemExit(0)
        except e:
            print(key, indict, jsonstruct, e)
            quit()

try:
    tree = json.load(open('tree.json'))

    output = [1, 0, {'progname': 'ncdutar', 'progver': '0.1', 'timestamp': int(time.time())}, [{'name': '/'}]]
    recurse(tree, output[3])

    json.dump(output, open('output.json', 'w'))
except FileNotFoundError:
    if len(sys.argv) > 1:
        generateTree(sys.argv[1])
    else:
        print("no input files supplied")
except ValueError:
    print("malformed tree.json, try removing it and regenerating it")

