## tsp_solver

> *Upper-case variables refer to command-line arguments. Please refer to Appendix A for details.

### The Algorithm


In a nutshell, this solver introduces a genetic algorithm using random mutations, along with simulated annealing in place to decrease the amount of mutations as more iterations are run. There is a threshold, calculated using the fitness rate `FITNESS`, which greedily decides whether or not an edge in the route is considered for mutation. This threshold becomes lower (i.e. more edges pass the threshold) after each iteration, which is where the simulated annealing comes to action.

First, a route is chosen out of the `BEST` best routes from the previous generation, based on the linear ranking discrete probability distribution. The fitness score for each edge in the route is simply its length. Each node that does not form any of the threshold-passing-edges are shuffled within the route to create a different (and hopefully a shorter) one. If this route is shorter than any of the best routes from the previous generation, it is inserted into the sorted "best routes" list to be sent on to the next generation. This choose-and-shuffle action is repeated for a `POPULATION` number of times per iteration.


#### Potential Faults in the Algorithm

As mentioned above, this algorithm represents a greedy algorithm that always favors edges with shorter lengths to be sent down to the next generation. A shorter edge does not always mean it contributes to a shorter route; ergo, there is a chance that it would converge to a local optimum without turning back. There are measures put in to prevent this as much as possible, such as the `POPULATION` parameter which allows for other mutations to get a chance to be compared, and the `BEST` parameter which allows for multiple routes, hopefully some that do not converge to local optima, to be sent down to the next generation.

This algorithm focuses on the ability to choose a "better" route based on previous calculations, not to pick the "best" route out there. Therefore, it is very unlikely that this algorithm will find the shortest answers to the problems.


### Appendix A: Command-line Arguments
`usage: tsp_solver.py [-h] [-b B] [-f F] [-p P] [-s S] [-v {0,1,2}] file`

#### Positional Arguments
`file`
> path of the .tsp file to be used for solving the TSP. Example files can be found [here](http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/index.html).

#### Optional Arguments
`-h, --help`
> shows the usage and argument descriptions and exits

`-b BEST (type: int, default: 100, 1 <= b)`
> number of best(shortest) routes to be used for next iteration

`-f FITNESS (type: float, default: 0.001, 0 < f <= 0.5)`
> fitness evaluation value f used for simulated annealing
>
> `temperature` is calculated as `f * time`, where time increases by 1 after each iteration, and the solver stops when `temperature == 1`.

`-p POPULATION (type: int, default: 1000, 1 <= p)`
> number of travel routes evaluated per iteration

`-s S (type: float, default: 0.5, 0 <= s <= 1)`
> parameter *s* used in linear ranking
>
> Probability p for an element of rank r (0 being the best) to be chosen out of n elements is `p = (1-s)/n + (r * s)/sum([1, ..., n])`

`-v, --verbose (type: int, default: 0, v in {0, 1, 2})`
> sets the verbosity; useful for debugging
>
> `0`: only prints out the final (i.e. shortest) distance found
<br> `1`: prints the distance every time a shorter one is found
<br> `2`: prints the various objects used during each iteration


### Appendix B: Classes and Methods

#### Node
###### Represents a node found in the .tsp files

Attributes: `id`, `x`, `y`

#### Edge
###### Represents an edge formed by connecting two Nodes

Attributes: `id`, `node_1`, `node_2`, `length`

#### Path
###### Represents a path formed by connecting adjacent Edges

Attributes: `edges`, `length`

`is_joinable_with_path(self, path)`
> If `self` is a path adjacent to `path`, returns `True`.

`join_with_path(self, path)`
> Joins the path `path` into `self`.

#### Route
###### Represents a full path formed by connecting all nodes in a single .tsp file

Attributes: `nodes`, `edges`, `sorted_edges`, `distance`

### Appendix C: Helper Functions

`nodes_to_edges(nodes)`
> `nodes`: list of N Nodes to be converted into N-1 Edges
>
> Returns a list of Edges by taking two consecutive Nodes from `nodes` at a time as each Edge's endpoints.

`edges_to_paths(edges)`
> `edges`: list of Edges to be converted into Paths
>
> It first obtains single-Edge Paths from each Edge, and joins any joinable (i.e. having overlapping ending Nodes) Path objects. It returns a list of all non-overlapping Paths found.

`flatten_to_nodes(iteration)`
> `iteration`: list containing Nodes, Edges, and/or Paths
>
> It return a list containing all the Nodes in the same order as in `iteration`, including the ones contained in Edges and Paths.

`verbose_print(*args, **kwargs)`
> This function sends the arguments to `print` when the cli argument `-v` is set to either `1` or `2`.

`very_verbose_print(*args, **kwargs)`
> Does the same as `verbose_print`, but only when `-v` is set to `2`.
