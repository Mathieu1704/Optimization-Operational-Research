import gurobipy as gp
from gurobipy import GRB
import numpy as np

def BMFRank1(X):
    m, n = X.shape

    # Modèle et Variables
    model = gp.Model()

    u = model.addVars(m, vtype=GRB.BINARY) #u[i] (ligne)
    v = model.addVars(n, vtype=GRB.BINARY) #v[j] (colonne)
    z = model.addVars(m, n, vtype=GRB.BINARY) #z[i,j] = u[i] * v[j]
    e = model.addVars(m, n, vtype=GRB.BINARY) #e[i,j] = |X[i,j] - z[i,j]|

    # Contraintes pour la linéarisation     
    for i in range(m):
        for j in range(n):
            # z[i,j] = u[i] * v[j]
            model.addConstr(z[i, j] <= u[i])
            model.addConstr(z[i, j] <= v[j])
            model.addConstr(z[i, j] >= u[i] + v[j] - 1)

            # e[i,j] >= |X[i,j] - z[i,j]|
            model.addConstr(e[i, j] >= X[i, j] - z[i, j])
            model.addConstr(e[i, j] >= z[i, j] - X[i, j])

    # Objectif 
    objectif = 0
    for i in range(m):
        for j in range(n):
            objectif += e[i, j]

    model.setObjective(objectif, GRB.MINIMIZE)

    #Résolution
    model.optimize()

    # Retourne u et v optimaux s’ils existent
    if model.status == GRB.OPTIMAL:
        u_sol = np.array([int(u[i].X) for i in range(m)])
        v_sol = np.array([int(v[j].X) for j in range(n)])
        return u_sol, v_sol
    else:
        print("Pas de solution optimale trouvée.")

#%% Test


X = np.array([
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [1, 1, 1, 1, 0]
])

u, v = BMFRank1(X)

print("u =", u)
print("v =", v)
print("uv^T =\n", np.outer(u, v))
print("||X -uv^T||_1 =", np.sum(np.abs(X - np.outer(u, v))))
