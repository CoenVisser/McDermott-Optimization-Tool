from pulp import *

x = LpVariable('x', 0, 3)
y = LpVariable('y', 0, 1)

prob = LpProblem('myProblem', LpMinimize)

prob += x + y <= 2

prob += -4*x + y

status = prob.solve()

print(LpStatus[status])

print(value(prob.objective))

print(f'optimal solution: x={value(x)}, y = {value(y)}. The minimum value is {-4 * value(x) + value(y)}')