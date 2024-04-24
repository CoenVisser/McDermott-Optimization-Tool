n = 6
m = 2

materials = ['Earth', 'Steel', 'Concrete'] 

required_materials = {
    (i, k): 100 for i in range(1, n + 1) for k in materials
}

test = {
    i: 100 for i in range(1, n + 1)
}

print(test)