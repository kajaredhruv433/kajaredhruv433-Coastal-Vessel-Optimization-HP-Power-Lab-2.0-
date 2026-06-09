import itertools
import pulp

INTEGER_TRIPS = False
ALLOW_TWO_PORT = True
MAX_UU_TIME_FOR_PAIR = 0.20


# -------------------------------------------------
# DATA
# -------------------------------------------------
def example_hpcl_instance():
    loading_ports = ["L1", "L2", "L3", "L4", "L5", "L6"]
    unloading_ports = ["U1","U2","U3","U4","U5","U6","U7","U8","U9","U10","U11"]
    tankers = ["T1","T2","T3","T4","T5","T6","T7","T8","T9"]

    tanker_capacity = {t: 50000 for t in tankers}
    tanker_capacity["T8"] = tanker_capacity["T9"] = 25000

    tanker_hire_rate = {
        "T1":0.63,"T2":0.49,"T3":0.51,"T4":0.51,"T5":0.53,
        "T6":0.57,"T7":0.65,"T8":0.39,"T9":0.38
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

    trip_time_UU = {u:{v:0.2 for v in unloading_ports} for u in unloading_ports}

    max_days_per_tanker = {t:30.0 for t in tankers}

    return locals()


# -------------------------------------------------
# NEAREST LOADING PORT
# -------------------------------------------------
def nearest_loading_time(unloading_ports, loading_ports, trip_time_LU):
    return {u: min(trip_time_LU[l][u] for l in loading_ports) for u in unloading_ports}


# -------------------------------------------------
# PATTERNS
# -------------------------------------------------
def build_patterns(data, return_same, return_nearest):
    nearest = nearest_loading_time(
        data["unloading_ports"], data["loading_ports"], data["trip_time_LU"]
    )

    patterns = []
    pid = 0

    for l in data["loading_ports"]:
        for u in data["unloading_ports"]:
            tt = data["trip_time_LU"][l][u]
            if return_same:
                tt += data["trip_time_LU"][l][u]
            if return_nearest:
                tt += nearest[u]

            patterns.append({
                "id": f"P{pid}",
                "load": l,
                "unloads": (u,),
                "time": tt
            })
            pid += 1

    return patterns


# -------------------------------------------------
# SOLVER
# -------------------------------------------------
def solve_scenario(return_same, return_nearest):
    data = example_hpcl_instance()
    patterns = build_patterns(data, return_same, return_nearest)

    model = pulp.LpProblem("HPCL", pulp.LpMinimize)

    x = pulp.LpVariable.dicts(
        "x",
        (data["tankers"], [p["id"] for p in patterns]),
        lowBound=0,
        cat="Continuous"
    )

    z = {}
    for t in data["tankers"]:
        for p in patterns:
            z[(t,p["id"])] = pulp.LpVariable(f"z_{t}_{p['id']}", lowBound=0)

    patt = {p["id"]:p for p in patterns}

    # Objective
    model += pulp.lpSum(
        data["tanker_hire_rate"][t] * patt[pid]["time"] * x[t][pid]
        for t in data["tankers"] for pid in patt
    )

    # Capacity
    for t in data["tankers"]:
        for pid in patt:
            model += z[(t,pid)] == data["tanker_capacity"][t] * x[t][pid]

    # Demand
    for u in data["unloading_ports"]:
        model += pulp.lpSum(
            z[(t,pid)]
            for t in data["tankers"]
            for pid in patt
            if patt[pid]["unloads"][0] == u
        ) >= data["demand"][u]

    # Time
    for t in data["tankers"]:
        model += pulp.lpSum(
            patt[pid]["time"] * x[t][pid] for pid in patt
        ) <= data["max_days_per_tanker"][t]

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return pulp.value(model.objective)


# -------------------------------------------------
# RUN 4 SCENARIOS
# -------------------------------------------------
if __name__ == "__main__":

    scenarios = [
        ("1 Loaded only (teleport)", False, False),
        ("2 Loaded + return same L", True, False),
        ("3 Loaded + nearest L", False, True),
        ("4 Loaded + UU + nearest L", True, True),
    ]

    print("\n================ RESULTS ================\n")
    for name, rs, rn in scenarios:
        cost = solve_scenario(rs, rn)
        print(f"{name:40s} Cost = {cost:.2f} Rs Cr")
