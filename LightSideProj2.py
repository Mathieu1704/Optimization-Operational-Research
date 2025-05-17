import gurobipy as gp
from gurobipy import GRB
import numpy as np

def flowshopwithtimelags(d, e, tlagsmin, tlagsmax):
    n = len(d[0])  # nombre de tâches
    m = len(d)     # nombre de machines

    model = gp.Model("Flowshop_with_Timelags")
    model.setParam("OutputFlag", 0)

    # Variables binaires x[i,j] = 1 si la tâche i est en position j dans la permutation
    x = model.addVars(n, n, vtype=GRB.BINARY)

    # Variables de début de chaque tâche sur chaque machine
    S = model.addVars(m, n, vtype=GRB.CONTINUOUS)

    # Variables binaires tard[i] = 1 si la tâche i est en retard
    tard = model.addVars(n, vtype=GRB.BINARY)

    # Contraintes : chaque tâche est assignée à une position
    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n)) == 1)

    # Contraintes : chaque position contient une tâche
    for j in range(n):
        model.addConstr(gp.quicksum(x[i, j] for i in range(n)) == 1)

    # Contraintes d'ordonnancement avec time lags
    M = 1e6
    for k in range(m):  # pour chaque machine
        for j in range(n):  # pour chaque position dans la permutation
            for i in range(n):
                for h in range(n):
                    if i != h:
                        model.addConstr(
                            S[k, i] >= S[k, h] + d[k][h] - M * (2 - x[i, j] - x[h, j - 1]) if j > 0 else 0
                        )

    # Contraintes de time lag entre machines
    for k in range(1, m):
        for i in range(n):
            model.addConstr(S[k, i] >= S[k-1, i] + d[k-1][i] + tlagsmin[k][i])
            model.addConstr(S[k, i] <= S[k-1, i] + d[k-1][i] + tlagsmax[k][i])

    # Contraintes de retard
    for i in range(n):
        model.addConstr(S[m-1, i] + d[m-1][i] <= e[i] + tard[i] * M)

    # Objectif : minimiser le nombre de tâches en retard
    model.setObjective(gp.quicksum(tard[i] for i in range(n)), GRB.MINIMIZE)

    model.optimize()

    # Retourner l'ordonnancement et le nombre de tâches en retard
    if model.status == GRB.OPTIMAL:
        ordonnancement = [-1] * n
        for i in range(n):
            for j in range(n):
                if x[i, j].X > 0.5:
                    ordonnancement[j] = i
        Ntmin = int(sum(tard[i].X for i in range(n)))
        return ordonnancement, Ntmin
    else:
        raise Exception("Aucune solution optimale trouvée.")
