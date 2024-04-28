import numpy as np
from scipy.spatial.distance import cdist
from math import ceil

from Extensions import vehicle

import pulp as plp

def optimization_tool(construction_coordinates, construction_sites_materials, storage_coordinates, materials, distances, max_storage_possible=10000):

    # materials = ['Earth', 'Steel', 'Concrete'] 

    # construction sites - information
    # construction_coordinates = np.array([[0, 0],
    #                                     [9, 0],
    #                                     [5, 4],
    #                                     [9, 8],
    #                                     [7, 6],
    #                                     [2, 7]])

    # construction_sites_materials = np.array([[2, 3, 4],
    #                             [1, 3, 2],
    #                             [0, 2, 3],
    #                             [2, 3, 0],
    #                             [1, 3, 2],
    #                             [4, 1, 1]]) * 1000 # tons to kg

    # # storage sites - information
    # storage_coordinates = np.array([[4, 3],
    #                                 [9, 5],
    #                                 [6, 9],
    #                                 [9, 2],
    #                                 [2, 3],
    #                                 [3, 5]])

    max_storage_possible = 10000
    max_storage_capacity = np.ones((storage_coordinates.shape[0], 1)) * max_storage_possible

    # materials setup
    n = construction_coordinates.shape[0]   # number of buildings
    m = storage_coordinates.shape[0]        # number of storage locations
    nr_mat = len(materials)
    mat_required = np.sum(construction_sites_materials, axis=0)

    required_materials = {(i, materials[k]): construction_sites_materials[i-1, k] for i in range(1, n + 1) for k in range(len(materials))}

    # vehicle setup
    earth_truck = vehicle(fuel_consumption=9.5, speed=10, material='Earth', capacity=700)
    steel_truck = vehicle(fuel_consumption=4.5, speed=10, material='Steel', capacity=300)
    concrete_truck = vehicle(fuel_consumption=6.5, speed=10, material='Concrete', capacity=400)

    vehicles = [earth_truck, steel_truck, concrete_truck]
    vehicle_capacity = {materials[k]: vehicles[k].capacity for k in range(nr_mat)}
    fuel_rate = {materials[k]: vehicles[k].fuel_consumption_per_meter for k in range(nr_mat)}


    # setup the minimization problem
    problem = plp.LpProblem('Minimize_Fuel_Consumption', plp.LpMinimize)


    # add the decision variables
    q = plp.LpVariable.dicts("q", [(i, j, k) for i in range(1, n + 1) for j in range(1, m + 1) for k in materials], lowBound=0)
    t = plp.LpVariable.dicts("t", [(i, j, k) for i in range(1, n + 1) for j in range(1, m + 1) for k in materials], lowBound=0, cat='Integer')
    y = {}
    for j in range(1, m + 1):
        for k in materials:
            y[(j, k)] = plp.LpVariable(f"y_({j},_'{k}')", cat='Binary')


    # add constraints
    # nr. 1: Material requirement constraint
    for i in range(1, n + 1):
        for k in materials:
            problem += plp.lpSum(q[(i, j, k)] for j in range(1, m + 1)) == required_materials[(i, k)], f"Material_Requirement_{i}_{k}"

    # nr. 2: Trip constraints
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            for k in materials:
                problem += t[(i, j, k)] * vehicle_capacity[k] >= q[(i, j, k)], f"Trip_Constraint_{i}_{j}_{k}"

    ##
    ##
    ## Constraint: Each storage site has either at least 30% or none of a given material
    BigM = 10000  # Large number for Big M constraint

    # Constraint for each material in each storage site
    for j in range(1, m + 1):
        for idx, k in enumerate(materials):
            # If y is 1, the storage site must hold at least 30% of the total required
            problem += plp.lpSum(q[(i, j, k)] for i in range(1, n + 1)) >= 0.333 * mat_required[idx] * y[(j, k)], f"Min_30_{j}_{k}"

            # If y is 0, the storage site holds none of the material
            problem += plp.lpSum(q[(i, j, k)] for i in range(1, n + 1)) <= BigM * y[(j, k)], f"Max_0_{j}_{k}"

    ##
    ##
    ## Constraint: quantity of all materials at each storage site does not exceed its capacity
    for j in range(1, m + 1):
        # Ensure total quantity of all materials at each storage site does not exceed its capacity
        problem += plp.lpSum(q[(i, j, k)] for i in range(1, n + 1) for k in materials) <= max_storage_capacity[j - 1], f"Storage_Capacity_{j}"
    ##
    ##
    ##



    # add objective function
    problem += plp.lpSum(t[(i, j, k)] * 2 * distances[(j-1, i-1)] * fuel_rate[k] for i in range(1, n + 1) for j in range(1, m + 1) for k in materials)


    # solve the problem
    problem.solve(plp.PULP_CBC_CMD())


    # get the status
    status = plp.LpStatus[problem.status]
    print(f"Status: {status}")


    # # output the results
    # for v in problem.variables():
    #     print(v.name, "=", v.varValue)


    # Output the objective function value
    print("Total Fuel Consumption =", plp.value(problem.objective))

    materials_array = np.zeros((n, m, len(materials)))
    trips_array = np.zeros((n, m, len(materials)))

    for variable in problem.variables():
        # Variable name example: q_(i)_(j)_(k) or t_(i)_(j)_(k)
        name = variable.name.split(",_")  # Split based on the defined naming structure
        var_value = variable.varValue

        # For q variables
        if name[0].startswith("q_"):
            i = int(name[0].split("_(")[1]) - 1  # Building index (1-based to 0-based)
            j = int(name[1]) - 1  # Storage index
            k = name[2].strip("')")  # Material name

            # Store material quantities in numpy array
            materials_array[i, j, materials.index(k)] = var_value

        # For t variables
        if name[0].startswith("t_"):
            i = int(name[0].split("_(")[1]) - 1  # Building index
            j = int(name[1]) - 1  # Storage index
            k = name[2].strip("')")  # Material name

            # Store trips data in numpy array
            trips_array[i, j, materials.index(k)] = var_value

    # print("Materials Array:")
    # print(materials_array)

    materials_per_site = np.sum(materials_array, axis=0)

    # print(materials_per_site)

    # print("Trips Array:")
    # print(trips_array)

    for index in range(m):
        print(f'Storage site {index+1} contains {materials_per_site[index, 0]} kg Earth, {materials_per_site[index, 1]} kg Steel, {materials_per_site[index, 2]} kg Concrete')

    return materials_per_site

