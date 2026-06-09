from copy import deepcopy

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
        "U11":{"U1":0.33,"U2":0.17,"U3":0.34,"U4":0.33,"U5":0.33,"U6":0.13,"U7":0.30,"U8":0.34,"U9":0.25,"U10":0.36,"U11":0.00}
    }

    max_days = 30.0
    return locals()


def best_next_move(current_pos, tanker, data, demand):
    best = None
    best_score = float("inf")

    cap = data["tanker_capacity"][tanker]
    rate = data["tanker_hire_rate"][tanker]

    for l in data["loading_ports"]:
        for u1 in data["unloading_ports"]:
            if demand[u1] <= 0:
                continue

            reposition = 0 if current_pos is None else data["trip_time_LU"][l][current_pos]
            sail1 = data["trip_time_LU"][l][u1]
            delivered1 = min(cap, demand[u1])
            total_delivered = delivered1
            total_time = reposition + sail1

            # single discharge option
            cost = total_time * rate
            score = cost / total_delivered
            if score < best_score:
                best_score = score
                best = (l, [u1], total_time, [delivered1], cost)

            # try second discharge port
            remaining_cap = cap - delivered1
            if remaining_cap > 0:
                for u2 in data["unloading_ports"]:
                    if u2 == u1 or demand[u2] <= 0:
                        continue

                    sail2 = data["trip_time_UU"][u1][u2]
                    delivered2 = min(remaining_cap, demand[u2])
                    total_delivered2 = delivered1 + delivered2
                    total_time2 = reposition + sail1 + sail2
                    cost2 = total_time2 * rate
                    score2 = cost2 / total_delivered2

                    if score2 < best_score:
                        best_score = score2
                        best = (l, [u1, u2], total_time2, [delivered1, delivered2], cost2)

    return best


def run_scheduler():
    data = example_hpcl_instance()
    demand = deepcopy(data["demand"])

    tanker_order = sorted(
        data["tanker_capacity"],
        key=lambda t: data["tanker_hire_rate"][t] / data["tanker_capacity"][t]
    )

    total_cost = 0.0
    schedule = {}

    for tanker in tanker_order:
        remaining_days = data["max_days"]
        current_pos = None
        path = []

        while remaining_days > 0 and any(demand[u] > 0 for u in demand):
            move = best_next_move(current_pos, tanker, data, demand)
            if move is None:
                break

            l, unload_ports, time_needed, deliveries, cost = move
            if time_needed > remaining_days:
                break

            remaining_days -= time_needed
            total_cost += cost

            for port, vol in zip(unload_ports, deliveries):
                demand[port] -= vol

            path.append({
                "Load": l,
                "Unload": unload_ports,
                "Delivered": deliveries,
                "Trip_days": round(time_needed,2),
                "Cost": round(cost,3)
            })

            current_pos = unload_ports[-1]

        if path:
            schedule[tanker] = path

        if not any(demand[u] > 0 for u in demand):
            break

    return schedule, total_cost, demand


if __name__ == "__main__":
    schedule, cost, remaining = run_scheduler()

    print("\n=========== OPTIMAL SCHEDULE ===========\n")
    for t, trips in schedule.items():
        print(f"\nTanker {t}")
        for step in trips:
            print(step)

    print("\n=========== SUMMARY ===========")
    print("Total Cost (Rs Cr):", round(cost,2))
    print("Remaining Demand:", remaining)
