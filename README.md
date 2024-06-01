Optimization software proposed as a solution for decarbonizing construction sites by the winning team of the 2024 McDermott R&D Business Challenge as part of the TU Delft Honours Programme.

---------------------------

We have developed a piece of software that aids the project planners by finding the optimal distribution of materials over a given construction site based on minimizing the utilization of the equipment used to transport these materials. This directly impacts the total fuel usage of each vehicle and, thus, also a significant portion of emissions and costs. For example, in case a certain construction site requires a certain amount of earth and steel and the equipment used to transport the earth requires far more fuel than the steel equipment per kg transported, the software will make the decision to place the steel at a storage site further away to make room at a nearby storage site for the earth


The software does the following:

1. Using Dijkstra’s algorithm, the shortest path between each storage site ‘node’ and each construction site ‘node’ is found
2. Next, this is fed into the optimization tool, which is constrained based on the data submitted by the user, this includes information, such as, the fuel consumption of each piece of equipment and the maximum storage capacity of each storage site. The objective of the tool is to minimize the following equation (i, j and k are integers representing the construction sites, storage sites and materials, respectively):
![Equation to be minimized](https://github.com/CoenVisser/McDermott/assets/150930345/6f474780-2964-4f15-8dcc-67c196483dba)
  - **t_i,j,k:** The amount of trips required to bring all of material ‘k’ from storage site ‘j’ to construction site ‘i’
  - **distances_(j, i):** the distance (calculated with Dijkstra’s algorithm) from storage site ‘j’ to construction site ‘i’
  - **fuel_rate_k:** the fuel consumption per meter driven of each the vehicle used to transport material ‘k’
