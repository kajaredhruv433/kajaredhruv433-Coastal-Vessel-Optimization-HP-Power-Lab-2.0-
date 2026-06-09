import itertools

try:
    import pulp
except ImportError:
    pulp = None

INTEGER_TRIPS = False

ALLOW_TWO_PORT = True

MAX_UU_TIME_FOR_PAIR = 0.20


def build_trip_patterns(loading_ports, unloading_ports, trip_time_LU, trip_time_UU,
                        allow_two_port_discharge=True,
                        max_uu_time_for_pair=None,
                        include_return=False):

    patterns = []
    pattern_id = 0

    # Single-port discharge patterns
    for l in loading_ports:
        for u in unloading_ports:
            base = trip_time_LU[l][u]
            if include_return:
                tt = base + trip_time_LU[l][u]
            else:
                tt = base
            patterns.append({
                "id": f"P{pattern_id}",
                "load_port": l,
                "unload_ports": (u,),
                "trip_time": tt,
            })
            pattern_id += 1

    # Two-port discharge patterns (pruned by distance)
    if allow_two_port_discharge:
        for l in loading_ports:
            for u1, u2 in itertools.permutations(unloading_ports, 2):
                if max_uu_time_for_pair is not None and trip_time_UU[u1][u2] > max_uu_time_for_pair:
                    continue  # only allow "close" pairs
                base1 = trip_time_LU[l][u1]
                leg12 = trip_time_UU[u1][u2]
                if include_return:
                    back = trip_time_LU[l][u2]  # approximate U2->L as L->U2
                    tt = base1 + leg12 + back
                else:
                    tt = base1 + leg12
                patterns.append({
                    "id": f"P{pattern_id}",
                    "load_port": l,
                    "unload_ports": (u1, u2),
                    "trip_time": tt,
                })
                pattern_id += 1

    return patterns


def solve_coastal_tanker_optimization(
    tankers,
    loading_ports,
    unloading_ports,
    tanker_capacity,
    tanker_hire_rate,
    demand,
    trip_time_LU,
    trip_time_UU,
    max_days_per_tanker,
    allow_two_port_discharge=True,
    full_loading=True,
    equality_demand=False,
    max_uu_time_for_pair=None,
    integer_trips=True,
    include_return=False,
):

    if pulp is None:
        raise ImportError("This script requires 'pulp'. Install it with: pip install pulp")

    # Build patterns
    patterns = build_trip_patterns(
        loading_ports, unloading_ports, trip_time_LU, trip_time_UU,
        allow_two_port_discharge=allow_two_port_discharge,
        max_uu_time_for_pair=max_uu_time_for_pair,
        include_return=include_return,
    )
    pattern_ids = [p["id"] for p in patterns]
    pattern_by_id = {p["id"]: p for p in patterns}

    print(f"\nBuilding model for include_return={include_return}. Trip patterns: {len(pattern_ids)}")

    # Create model
    model = pulp.LpProblem("Coastal_Tanker_Optimization", pulp.LpMinimize)

    # Decision variables: number of trips for each tanker & pattern
    x_cat = "Integer" if integer_trips else "Continuous"
    x = pulp.LpVariable.dicts("x", (tankers, pattern_ids), lowBound=0, cat=x_cat)

    # Cargo allocation variables
    z = {}  # single-port patterns
    y = {}  # two-port patterns
    for t in tankers:
        for pid in pattern_ids:
            patt = pattern_by_id[pid]
            ups = patt["unload_ports"]
            if len(ups) == 1:
                z[(t, pid)] = pulp.LpVariable(f"z_{t}_{pid}", lowBound=0)
            else:
                for u in ups:
                    y[(t, pid, u)] = pulp.LpVariable(f"y_{t}_{pid}_{u}", lowBound=0)

    model += pulp.lpSum(
        tanker_hire_rate[t] * pattern_by_id[pid]["trip_time"] * x[t][pid]
        for t in tankers for pid in pattern_ids
    ), "TotalCost"

    for t in tankers:
        cap = tanker_capacity[t]
        for pid in pattern_ids:
            patt = pattern_by_id[pid]
            ups = patt["unload_ports"]
            if len(ups) == 1:
                if full_loading:
                    model += z[(t, pid)] == cap * x[t][pid]
                else:
                    model += z[(t, pid)] <= cap * x[t][pid]
            else:
                if full_loading:
                    model += pulp.lpSum(y[(t, pid, u)] for u in ups) == cap * x[t][pid]
                else:
                    model += pulp.lpSum(y[(t, pid, u)] for u in ups) <= cap * x[t][pid]

    for u in unloading_ports:
        incoming = []
        for t in tankers:
            for pid in pattern_ids:
                patt = pattern_by_id[pid]
                ups = patt["unload_ports"]
                if len(ups) == 1 and ups[0] == u:
                    incoming.append(z[(t, pid)])
                elif len(ups) == 2 and u in ups:
                    incoming.append(y[(t, pid, u)])
        if equality_demand:
            model += pulp.lpSum(incoming) == demand[u], f"Demand_{u}"
        else:
            model += pulp.lpSum(incoming) >= demand[u], f"Demand_{u}"

    for t in tankers:
        model += pulp.lpSum(
            pattern_by_id[pid]["trip_time"] * x[t][pid] for pid in pattern_ids
        ) <= max_days_per_tanker[t], f"TimeLimit_{t}"

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=True)
    model.solve(solver)

    status = pulp.LpStatus[model.status]
    total_cost = pulp.value(model.objective)

    # Collect statistics
    solution_rows = []
    tanker_days = {t: 0.0 for t in tankers}
    tanker_volume = {t: 0.0 for t in tankers}

    for t in tankers:
        for pid in pattern_ids:
            trips = x[t][pid].value()
            if trips is None or trips <= 1e-6:
                continue
            patt = pattern_by_id[pid]
            load_port = patt["load_port"]
            ups = patt["unload_ports"]
            tt = patt["trip_time"]
            cost_trip = tanker_hire_rate[t] * tt
            tanker_days[t] += tt * trips

            if len(ups) == 1:
                u = ups[0]
                vol = z[(t, pid)].value()
                tanker_volume[t] += vol
                solution_rows.append({
                    "Tanker": t,
                    "LoadingPort": load_port,
                    "UnloadingPorts": " -> ".join(ups),
                    "Trips": trips,
                    "Volume_to_U1": vol,
                    "Volume_to_U2": 0.0,
                    "TripTime_days": tt,
                    "Cost_per_trip_Cr": cost_trip,
                    "Total_cost_Cr": cost_trip * trips,
                })
            else:
                u1, u2 = ups
                v1 = y[(t, pid, u1)].value()
                v2 = y[(t, pid, u2)].value()
                tanker_volume[t] += (v1 + v2)
                solution_rows.append({
                    "Tanker": t,
                    "LoadingPort": load_port,
                    "UnloadingPorts": " -> ".join(ups),
                    "Trips": trips,
                    "Volume_to_U1": v1,
                    "Volume_to_U2": v2,
                    "TripTime_days": tt,
                    "Cost_per_trip_Cr": cost_trip,
                    "Total_cost_Cr": cost_trip * trips,
                })

    solution_rows.sort(key=lambda r: (r["Tanker"], r["LoadingPort"], r["UnloadingPorts"]))

    stats = {
        "status": status,
        "total_cost": total_cost,
        "tanker_days": tanker_days,
        "tanker_volume": tanker_volume,
        "solution_rows": solution_rows,
    }
    return stats


def example_hpcl_instance():
    """
    Your HPCL instance as data dictionaries
    """
    loading_ports = ["L1", "L2", "L3", "L4", "L5", "L6"]
    unloading_ports = ["U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "U10", "U11"]
    tankers = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"]

    tanker_capacity = {
        "T1": 50000,
        "T2": 50000,
        "T3": 50000,
        "T4": 50000,
        "T5": 50000,
        "T6": 50000,
        "T7": 50000,
        "T8": 25000,
        "T9": 25000,
    }

    tanker_hire_rate = {
        "T1": 0.63,
        "T2": 0.49,
        "T3": 0.51,
        "T4": 0.51,
        "T5": 0.53,
        "T6": 0.57,
        "T7": 0.65,
        "T8": 0.39,
        "T9": 0.38,
    }

    demand = {
        "U1": 40000,
        "U2": 135000,
        "U3": 5000,
        "U4": 20000,
        "U5": 20000,
        "U6": 20000,
        "U7": 110000,
        "U8": 30000,
        "U9": 20000,
        "U10": 20000,
        "U11": 20000,
    }

    trip_time_LU = {
        "L1": {"U1":0.4,"U2":0.7,"U3":0.4,"U4":0.4,"U5":0.4,"U6":0.6,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.7},
        "L2": {"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.5,"U11":0.6},
        "L3": {"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.6,"U11":0.6},
        "L4": {"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.6},
        "L5": {"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.5},
        "L6": {"U1":0.58,"U2":0.73,"U3":0.64,"U4":0.56,"U5":0.56,"U6":0.65,"U7":0.67,"U8":0.64,"U9":0.50,"U10":0.70,"U11":0.73},
    }

    trip_time_UU = {
        "U1":{"U1":0.00,"U2":0.35,"U3":0.19,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.23,"U8":0.19,"U9":0.09,"U10":0.19,"U11":0.33},
        "U2":{"U1":0.36,"U2":0.00,"U3":0.38,"U4":0.37,"U5":0.37,"U6":0.15,"U7":0.34,"U8":0.38,"U9":0.29,"U10":0.40,"U11":0.19},
        "U3":{"U1":0.16,"U2":0.33,"U3":0.00,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.21,"U8":0.17,"U9":0.09,"U10":0.19,"U11":0.32},
        "U4":{"U1":0.18,"U2":0.37,"U3":0.21,"U4":0.00,"U5":0.12,"U6":0.29,"U7":0.25,"U8":0.21,"U9":0.05,"U10":0.21,"U11":0.35},
        "U5":{"U1":0.18,"U2":0.37,"U3":0.21,"U4":0.12,"U5":0.00,"U6":0.29,"U7":0.25,"U8":0.21,"U9":0.05,"U10":0.21,"U11":0.35},
        "U6":{"U1":0.29,"U2":0.17,"U3":0.32,"U4":0.31,"U5":0.31,"U6":0.00,"U7":0.22,"U8":0.32,"U9":0.24,"U10":0.34,"U11":0.18},
        "U7":{"U1":0.19,"U2":0.29,"U3":0.21,"U4":0.20,"U5":0.20,"U6":0.15,"U7":0.00,"U8":0.21,"U9":0.12,"U10":0.21,"U11":0.28},
        "U8":{"U1":0.16,"U2":0.33,"U3":0.17,"U4":0.16,"U5":0.16,"U6":0.25,"U7":0.21,"U8":0.00,"U9":0.09,"U10":0.19,"U11":0.32},
        "U9":{"U1":0.17,"U2":0.37,"U3":0.21,"U4":0.12,"U5":0.12,"U6":0.29,"U7":0.25,"U8":0.21,"U9":0.00,"U10":0.21,"U11":0.35},
        "U10":{"U1":0.14,"U2":0.34,"U3":0.18,"U4":0.15,"U5":0.15,"U6":0.27,"U7":0.20,"U8":0.18,"U9":0.07,"U10":0.00,"U11":0.33},
        "U11":{"U1":0.33,"U2":0.17,"U3":0.34,"U4":0.33,"U5":0.33,"U6":0.13,"U7":0.30,"U8":0.34,"U9":0.25,"U10":0.36,"U11":0.00},
    }

    max_days_per_tanker = {t: 30.0 for t in tankers}

    return {
        "tankers": tankers,
        "loading_ports": loading_ports,
        "unloading_ports": unloading_ports,
        "tanker_capacity": tanker_capacity,
        "tanker_hire_rate": tanker_hire_rate,
        "demand": demand,
        "trip_time_LU": trip_time_LU,
        "trip_time_UU": trip_time_UU,
        "max_days_per_tanker": max_days_per_tanker,
    }


if __name__ == "__main__":
    data = example_hpcl_instance()

    # === Scenario 1: LOADED LEGS ONLY ===
    res_loaded = solve_coastal_tanker_optimization(
        integer_trips=INTEGER_TRIPS,
        include_return=False,
        allow_two_port_discharge=ALLOW_TWO_PORT,
        max_uu_time_for_pair=MAX_UU_TIME_FOR_PAIR,
        **data,
    )

    print("\n=== SCENARIO 1: LOADED LEGS ONLY ===")
    print("Status:", res_loaded["status"])
    print("Total cost (Rs Cr):", res_loaded["total_cost"])
    print("Tanker days used:", res_loaded["tanker_days"])
    print("Tanker volume moved (MT):", res_loaded["tanker_volume"])
    print("Sample trips:")
    for row in res_loaded["solution_rows"][:10]:
        print(row)

    res_full = solve_coastal_tanker_optimization(
        integer_trips=INTEGER_TRIPS,
        include_return=True,
        allow_two_port_discharge=ALLOW_TWO_PORT,
        max_uu_time_for_pair=MAX_UU_TIME_FOR_PAIR,
        **data,
    )

    print("\n=== SCENARIO 2: LOADED + RETURN LEGS ===")
    print("Status:", res_full["status"])
    print("Total cost (Rs Cr):", res_full["total_cost"])
    print("Tanker days used:", res_full["tanker_days"])
    print("Tanker volume moved (MT):", res_full["tanker_volume"])
    print("Sample trips:")
    for row in res_full["solution_rows"][:10]:
        print(row)
