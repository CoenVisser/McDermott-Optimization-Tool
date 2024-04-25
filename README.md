McDermott Utilization Optimization Code

The main optimization code can be found in Optimization_Tool.py, it uses the 'vehicles' object from Extensions.py

Hopefully, it'll soon be possible to link the user interface to the optimization tool

-------------------
Problem description:
Imagine you've got n buildings to be built and m storage locations for the necessary materials. These buildings and storage locations are fixed and scattered on a large plot of land. Each storage location can hold an certain (tbd, maybe user input) maximum amount of materials. Each building requires a set amount of each material. Each materials has an associated vehicle that is used to transport it. Each of these vehicles has a specific fuel consumption. Also, each vehicle has a limited carrying capacity. We want to determine what is the best distribution of the materials over the m storage locations. The best distribution of materials is based on the distribution that minimizes the total fuel consumption of all vehicles.

We aim to build a tool that is able to automatically determine this distribution. The tool should be able to take a plotplan, which can then be annotated by the used to tell the program the coordinates of the storage locations, the buildings and the road layout. Afterwards, the tool will determine, using a (still undetermined) algorithm, the shortest path between each of the storage locations and each of the buildings. Next, the user has to fill in the required materials per building and the properties of the vehicles used to transport them. This information is then fed into the tool. The tool then returns the optimal distribution of materials over the different storage locations. 

The decision variables are as follows:

$q_{ijk}$​: Total quantity of material k transported from storage location j to building i.

$t_{ijk}$: Number of trips to transport material k from storage location j to building i.



The objective function (to be minimized) is as follows:
$`F= \sum_{i=1}^n \sum_{j=1}^{m} \sum_{k=1}^{l  } t_{i, j, k} \times 2 \times \text{distance}(j, i) \times \text{fuel\_rate}(k)`$
-------------------
