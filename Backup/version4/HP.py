from copy import deepcopy
import pulp


def example_hpcl_instance():
    loading_ports = ["L1","L2","L3","L4","L5","L6"]
    unloading_ports = ["U1","U2","U3","U4","U5","U6","U7","U8","U9","U10","U11"]

    tanker_capacity = {
        "T1":50000,"T2":50000,"T3":50000,"T4":50000,
        "T5":50000,"T6":50000,"T7":50000,"T8":25000,"T9":25000
    }

    tanker_hire_rate = {
        "T1":0.63,"T2":0.49,"T3":0.51,"T4":0.51,
        "T5":0.53,"T6":0.57,"T7":0.65,"T8":0.39,"T9":0.38
    }

    demand = {
        "U1":40000,"U2":135000,"U3":5000,"U4":20000,"U5":20000,
        "U6":20000,"U7":110000,"U8":30000,"U9":20000,
        "U10":20000,"U11":20000
    }

    trip_time_LU = {
        "L1":{"U1":0.4,"U2":0.7,"U3":0.4,"U4":0.4,"U5":0.4,"U6":0.6,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.7},
        "L2":{"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.5,"U11":0.6},
        "L3":{"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.6,"U11":0.6},
        "L4":{"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.6},
        "L5":{"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.5},
        "L6":{"U1":0.58,"U2":0.73,"U3":0.64,"U4":0.56,"U5":0.56,"U6":0.65,"U7":0.67,"U8":0.64,"U9":0.50,"U10":0.70,"U11":0.73}
    }

    trip_time_UU = {
        "U1":{"U2":0.35,"U3":0.19,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.23,"U8":0.19,"U9":0.09,"U10":0.19,"U11":0.33},
        "U2":{"U1":0.36,"U3":0.38,"U4":0.37,"U5":0.37,"U6":0.15,"U7":0.34,"U8":0.38,"U9":0.29,"U10":0.40,"U11":0.19},
        "U3":{"U1":0.16,"U2":0.33,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.21,"U8":0.17,"U9":0.09,"U10":0.19,"U11":0.32},
        "U4":{"U1":0.18,"U2":0.37,"U3":0.21,"U5":0.12,"U6":0.29,"U7":0.25,"U8":0.21,"U9":0.05,"U10":0.21,"U11":0.35},
        "U5":{"U1":0.18,"U2":0.37,"U3":0.21,"U4":0.12,"U6":0.29,"U7":0.25,"U8":0.21,"U9":0.05,"U10":0.21,"U11":0.35},
        "U6":{"U1":0.29,"U2":0.17,"U3":0.32,"U4":0.31,"U5":0.31,"U7":0.22,"U8":0.32,"U9":0.24,"U10":0.34,"U11":0.18},
        "U7":{"U1":0.19,"U2":0.29,"U3":0.21,"U4":0.20,"U5":0.20,"U6":0.15,"U8":0.21,"U9":0.12,"U10":0.21,"U11":0.28},
        "U8":{"U1":0.16,"U2":0.33,"U3":0.17,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.21,"U9":0.09,"U10":0.19,"U11":0.32},
        "U9":{"U1":0.17,"U2":0.37,"U3":0.21,"U4":0.12,"U5":0.12,"U6":0.29,"U7":0.25,"U8":0.21,"U10":0.21,"U11":0.35},
        "U10":{"U1":0.14,"U2":0.34,"U3":0.18,"U4":0.15,"U5":0.15,"U6":0.27,"U7":0.20,"U8":0.18,"U9":0.07,"U11":0.33},
        "U11":{"U1":0.33,"U2":0.17,"U3":0.34,"U4":0.33,"U5":0.33,"U6":0.13,"U7":0.30,"U8":0.34,"U9":0.25,"U10":0.36}
    }

    max_days = 30.0
    return locals()


def optimize_schedule():
    data = example_hpcl_instance()

    prob = pulp.LpProblem("HPCL_Optimization", pulp.LpMinimize)

    y = {}

    for t in data["tanker_capacity"]:
        for l in data["loading_ports"]:
            for u1 in data["unloading_ports"]:
                y[(t,l,u1,None)] = pulp.LpVariable(f"y_{t}_{l}_{u1}", lowBound=0, cat="Integer")

                for u2 in data["unloading_ports"]:
                    if u1 != u2:
                        y[(t,l,u1,u2)] = pulp.LpVariable(f"y_{t}_{l}_{u1}_{u2}", lowBound=0, cat="Integer")

    # Objective
    prob += pulp.lpSum(
        data["tanker_hire_rate"][t] *
        (data["trip_time_LU"][l][u1] + (data["trip_time_UU"][u1][u2] if u2 else 0)) *
        y[(t,l,u1,u2)]
        for (t,l,u1,u2) in y
    )

    # Demand constraints
    for u in data["unloading_ports"]:
        prob += pulp.lpSum(
            data["tanker_capacity"][t] * y[(t,l,u1,u2)]
            for (t,l,u1,u2) in y if u1 == u or u2 == u
        ) >= data["demand"][u]

    # Tanker working days
    for t in data["tanker_capacity"]:
        prob += pulp.lpSum(
            (data["trip_time_LU"][l][u1] + (data["trip_time_UU"][u1][u2] if u2 else 0)) *
            y[(t,l,u1,u2)]
            for (tt,l,u1,u2) in y if tt == t
        ) <= data["max_days"]

    prob.solve()

    print("\nMinimum Achievable Cost:", round(pulp.value(prob.objective),3))

    for k,v in y.items():
        if v.varValue and v.varValue > 0:
            print(k, "Trips:", int(v.varValue))


if __name__ == "__main__":
    optimize_schedule()
