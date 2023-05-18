# This program solves the Stigler Diet Program
# The problem was studied by the first time by the Nobel laureate Stigler as a family of problem
# He didn't mean to recommed a diet but to illustrate an economics general problem.

# The idea is that there exist a minimum quantities of nutrients and calories that have
# to be met by everyday ingestion. These quantities are reflected in the table 'nutrients'
# in the data.py file.
# There are known quantities of all these nutrients in a set of foods as reflected in the table
# 'data' in the file data.py.

# We will use ortools to solve this problem
# ortools have been developed by Google to solve many kinds of mathematical programming (optimization) problems
from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit

# We import the file data.py to have access to the definitions in this file
from data import * 

# Create the linear solver with the GLOP backend.
# GLOP is an open source solver which can be used freely
solver = pywraplp.Solver.CreateSolver('GLOP')
if not solver:
    exit

# Variables are defined using solver.Numvar. You can create individual variables like
# in the commented sample below
# Create the variables x and y.
#   x = solver.NumVar(0, solver.infinity(), 'x')
#   y = solver.NumVar(0, solver.infinity(), 'y')
# The parameters of NumVar are:
#   - minimum value
#   - maximum value
#   - name of variable

# Because this function is general we could create the variables in an array, to hold
# a large number of variables, declaring an array to hold our variables. Note that
# item[0] holds the name of each food in the 'data' table. The variables itself will hold
# the quantity of each item
foods = [solver.NumVar(0.0, solver.infinity(), item[0]) for item in data]

print('Number of variables =', solver.NumVariables())

# The constraints are reprsented as a matrix where each variable holds
# a coefficient in the linear combination of all constraints. This linear combination
# must fullfill the constraint of being between two values. 
# Let's have a look at one example 0 <= 2*x + y <= 5.
#ct = solver.Constraint(0, 5, 'ct')
#ct.SetCoefficient(x, 2)
#ct.SetCoefficient(y, 1)

# The constrainsts can be reprsented as arrays to make evrything easier
# Create the constraints, one per nutrient.
constraints = []
for i, nutrient in enumerate(nutrients):
    # Append one constrint per nutrient. If you look at the nutrient table,
    # you will see that the minimum value is stored at nurient[1] (second column)
    constraints.append(solver.Constraint(nutrient[1], solver.infinity()))

    # The coefficients in this constraint are given by the 'data' table
    # The variable for which we are creating the coefficient is foods[j]
    # The coefficient itself has the value of the corresponding nutrient in 'data'
    # table, which is located at position i + 3 (where i is the nutrient number)
    for j, item in enumerate(data):
        constraints[i].SetCoefficient(foods[j], item[i + 3])

print('Number of constraints =', solver.NumConstraints())

# Finally, we set the objective function
# As usual, let's see in comments a simple objective function for two variables
# Again, we specify the coefficients of each variable for the linear combination of all variables
# Create the objective function, 3 * x + y.
#   objective = solver.Objective()
#   objective.SetCoefficient(x, 3)
#   objective.SetCoefficient(y, 1)
#   objective.SetMaximization()

# Let's translate this to our problem
# Objective function: Minimize the sum of foods cost. 
# The objective function is the sum of each variable (food quantity) multiplied 
# by its cost (cost is in column 3). The costs are the coefficients
objective = solver.Objective()
for f, food in enumerate(foods):
    objective.SetCoefficient(food, data[f][2]) # 2 is column 3
objective.SetMinimization()

status = solver.Solve()

print()
# Check that the problem has an optimal solution.
if status != solver.OPTIMAL:
    print('The problem does not have an optimal solution!')
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')
        exit(1)
else:
    print('Optimal solution found')

# Display the amounts to purchase of each food.
nutrients_result = [0] * len(nutrients)
print('\nDaily Foods:')
for i, food in enumerate(foods):
    if food.solution_value() > 0.0:
        print('{}: {}'.format(data[i][0], food.solution_value()))
        for j, _ in enumerate(nutrients):
            nutrients_result[j] += data[i][j + 3] * food.solution_value()

print('\nOptimal cost: ${:.4f}'.format(objective.Value()))

print('\nNutrients per day:')
for i, nutrient in enumerate(nutrients):
    print('{}: {:.2f} (min {})'.format(nutrient[0], nutrients_result[i], nutrient[1]))
