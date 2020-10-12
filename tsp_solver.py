################################################################
'''
NOTE: Descriptions for command-line arguments, classes, and
helper functions are only included in the documentation report.
'''
################################################################

import argparse
import random

DEFAULT_BEST_ROUTES = 100
DEFAULT_FITNESS_EVALUATION_RATE = 0.001
DEFAULT_POPULATION = 1000
DEFAULT_S_PARAMETER = 0.5

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="path of the .tsp file")
parser.add_argument("-b", type=int, default=DEFAULT_BEST_ROUTES, help="number of best(shortest) routes to be used for next iteration; default = {}".format(DEFAULT_BEST_ROUTES))
parser.add_argument("-f", type=float, default=DEFAULT_FITNESS_EVALUATION_RATE, help="fitness evaluation rate f, which is used as the rate of simulated annealing; default = {} (0 < f <= 0.5)".format(DEFAULT_FITNESS_EVALUATION_RATE))
parser.add_argument("-p", type=int, default=DEFAULT_POPULATION, help="number of travel routes evaluated per iteration; default = {}".format(DEFAULT_POPULATION))
parser.add_argument("-s", type=float, default=DEFAULT_S_PARAMETER, help="parameter value s used for linear ranking of best routes; default = {} (0 <= s <= 1)".format(DEFAULT_S_PARAMETER))
parser.add_argument("-v", "--verbose", type=int, default=0, choices=[0, 1, 2], help="prints [2] details for each iteration, [1] shortest distance when a new one is found, [0] final distance")
args = parser.parse_args()
verbose = args.verbose


def verbose_print(*args, **kwargs):
    if verbose >= 1:
        print(*args, **kwargs)


def very_verbose_print(*args, **kwargs):
    if verbose == 2:
        print(*args, **kwargs)


class Node:
    def __init__(self, node_list):
        id, x, y = node_list
        self.id = id
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Node {}: ({}, {})".format(self.id, self.x, self.y)


class Edge:
    def __init__(self, id, node_1, node_2):
        self.id = id
        self.node_1 = node_1
        self.node_2 = node_2
        d_x = node_1.x - node_2.x
        d_y = node_1.y - node_2.y
        self.length = (d_x**2 + d_y**2)**(1/2)

    def __repr__(self):
        return "Edge {} -> {} with length {}".format(self.node_1.id, self.node_2.id, self.length)


class Path:
    def __init__(self, edge):
        self.edges = [edge]
        self.length = edge.length

    def is_joinable_with_path(self, path):
        right_joinable = self.edges[-1].node_2.id == path.edges[0].node_1.id
        left_joinable = self.edges[0].node_1.id == path.edges[-1].node_2.id
        return right_joinable or left_joinable

    def join_with_path(self, path):
        if self.edges[-1].node_2.id == path.edges[0].node_1.id:
            self.edges += path.edges
            self.length += path.length
        elif self.edges[0].node_1.id == path.edges[-1].node_2.id:
            self.edges = path.edges + self.edges
            self.length += path.length
        else:
            raise Exception("Paths {} and {} do not connect.".format(self, path))

    def __repr__(self):
        _edges_str = []
        for edge in self.edges:
            _edges_str.append(edge.node_1.id)
        _edges_str.append(self.edges[-1].node_2.id)
        edges_str = " -> ".join(_edges_str)
        return "Path {} with length {}".format(edges_str, self.length)


class Route():
    def __init__(self, nodes, shuffle = False):
        if shuffle: random.shuffle(nodes)
        edges = nodes_to_edges(nodes)
        self.nodes = nodes
        self.edges = edges
        self.sorted_edges = sorted(edges, key=lambda edge: edge.length)
        self.distance = sum([edge.length for edge in edges])


def nodes_to_edges(nodes):
    edges = []
    id = 0
    for node_1, node_2 in zip(nodes[:-1], nodes[1:]):
        edges.append(Edge(id, node_1, node_2))
        id += 1
    return edges


def edges_to_paths(edges):
    paths = []
    no_paths_added = True
    while len(edges) > 0:
        if no_paths_added:
            paths.append(Path(edges.pop()))
        no_paths_added = True
        for path in paths:
            for edge in edges:
                temp_path = Path(edge)
                if path.is_joinable_with_path(temp_path):
                    path.join_with_path(temp_path)
                    edges.remove(edge)
                    no_paths_added = False
    return paths


def flatten_to_nodes(iteration):
    nodes = []
    for elem in iteration:
        if type(elem) == Node:
            nodes.append(elem)
        elif type(elem) == Edge:
            nodes.append(elem.node_1)
            nodes.append(elem.node_2)
        elif type(elem) == Path:
            for edge in elem.edges:
                nodes.append(edge.node_1)
            nodes.append(elem.edges[-1].node_2)
        else:
            raise Exception("Cannot convert '{}' to Node(s).".format(elem))
    return nodes


def tsp(nodes, anneal_rate, population, best_num, s):

    # Obtain probability distribution for linear ranking
    sum_best_num = sum(range(best_num + 1))
    p_distribution = [(1-s)/best_num + (i * s)/sum_best_num for i in range(best_num)]

    # Initial variables
    _best_routes = [Route(nodes, shuffle = True) for _ in range(best_num)]
    best_routes = sorted(_best_routes, key=lambda route: route.distance) # For now, this is just a list of random Routes sorted by distance.
    time = 1
    temperature = anneal_rate * time

    while temperature < 1:
        pass_threshold = int(len(nodes) * temperature) # pass_threshold is the number of edges excempt from shuffling. It increases as more iterations happen (simulated annealing)

        # Continue through the loop until threshold is at least 1.
        if pass_threshold < 1:
            time += 1
            temperature = anneal_rate * time
            continue
        elif pass_threshold == len(nodes):
            break

        very_verbose_print("{:.2f}% done".format((temperature + anneal_rate) * 100))

        _best_nodes_segregated = [] # All Edges that pass the threshold are saved separately as Paths in this list.

        # Reiterate for each best_route from previous generation.
        for route in best_routes:

            # Segregate the shortest edges that pass the threshold
            pass_edges = route.sorted_edges[:pass_threshold]
            very_verbose_print("Shortest {} edge(s): {}".format(pass_threshold, pass_edges))

            nodes = route.nodes[:] # This list will contain the nodes that did not pass the threshold (target for reshuffling)

            for edge in pass_edges:
                if edge.node_1 in nodes:
                    nodes.remove(edge.node_1)
                if edge.node_2 in nodes:
                    nodes.remove(edge.node_2)

            pass_paths = edges_to_paths(pass_edges) # All Edges are converted to Paths, with adjacent Paths joined together. This is done to prevent Nodes from reappearing in the Route.
            very_verbose_print("Shortest edges to path(s): {}".format(pass_paths))

            _nodes_segregated = nodes + pass_paths
            _best_nodes_segregated.append(_nodes_segregated) # _nodes_segregated is now a list ready for shuffling (i.e. mutating.)

        for _ in range(population):
            _nodes_segregated = random.choices(_best_nodes_segregated, p_distribution)[0][:] # Pick out a _nodes_segregated by the probability distribution based on linear ranking
            random.shuffle(_nodes_segregated)
            new_nodes = flatten_to_nodes(_nodes_segregated) # This is now a list of only Nodes.
            very_verbose_print("New route: {}".format(new_nodes))

            new_route = Route(new_nodes) # Convert the Nodes into a Route object
            very_verbose_print("New distance = {}".format(new_route.distance))

            # For each new Route, check if it qualifies to pass on to the next generation.
            for i, route in enumerate(best_routes):
                if new_route.distance < route.distance:
                    best_routes.insert(i, new_route)
                    best_routes.pop()
                    if i == 0: verbose_print("New shortest distance found: {}".format(new_route.distance))
                    break
                else:
                    very_verbose_print("Route {} discarded.".format(new_route))

        # End of one iteration (i.e. generation.)
        time += 1
        temperature = anneal_rate * time # In this algorithm, this variable increases as it "cools down." I probably should have chosen a more appropriate name.

    best_route = best_routes[0]
    best_distance = best_route.distance
    print(best_distance)

    # Write solution file.
    with open('solution.csv', 'w') as solution:
        for node in best_route.nodes:
            solution.write(node.id + '\n')
        solution.close()

# Parse the .tsp file into a list of Nodes which is pass down along with command-line arguments to the solver function.
def __main__():
    filename = args.file
    anneal_rate = args.f
    population = args.p
    best_num = args.b
    s = args.s

    def parse(_node):
        node = _node.strip().split()
        return Node(node[0], node[1], node[2])

    filename = args.file
    nodes = []
    with open(filename, 'r') as file:
        _nodes = file.readlines()[6:]
        file.close()
        for _node in _nodes:
            if _node.strip() == "EOF":
                break
            nodes.append(Node(_node.strip().split()))

    tsp(nodes, anneal_rate, population, best_num, s)

__main__()
