from copy import deepcopy

# =========================================================
# DATA
# =========================================================
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

    max_days = 30.0

    return locals()


# =========================================================
# GLOBAL-BEST MOVE SELECTION
# =========================================================
def best_next_move(current_pos, tanker, data, demand):
    best = None
    best_score = float("inf")

    cap = data["tanker_capacity"][tanker]
    rate = data["tanker_hire_rate"][tanker]

    for l in data["loading_ports"]:
        for u in data["unloading_ports"]:
            if demand[u] <= 0:
                continue

            if current_pos is None:
                reposition = 0
            else:
                reposition = data["trip_time_LU"][l][current_pos]

            sail = data["trip_time_LU"][l][u]
            total_time = reposition + sail

            delivered = min(cap, demand[u])
            cost = total_time * rate
            score = cost / delivered  # Rs per MT

            if score < best_score:
                best_score = score
                best = (l, u, total_time, delivered, cost)

    return best


# =========================================================
# MAIN SCHEDULER
# =========================================================
def run_scheduler():
    data = example_hpcl_instance()
    demand = deepcopy(data["demand"])

    # Tankers sorted by efficiency (Rs / MT-day)
    tanker_order = sorted(
        data["tanker_capacity"],
        key=lambda t: data["tanker_hire_rate"][t] / data["tanker_capacity"][t]
    )

    tanker_state = {}
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

            l, u, time_needed, delivered, cost = move
            if time_needed > remaining_days:
                break

            remaining_days -= time_needed
            demand[u] -= delivered
            total_cost += cost

            path.append({
                "Load": l,
                "Unload": u,
                "Delivered_MT": delivered,
                "Trip_days": round(time_needed, 2),
                "Cost_RsCr": round(cost, 3)
            })

            current_pos = u

        if path:
            schedule[tanker] = path

        if not any(demand[u] > 0 for u in demand):
            break

    return schedule, total_cost, demand


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    schedule, cost, remaining = run_scheduler()

    print("\n================ OPTIMAL SCHEDULE ================\n")
    for t, trips in schedule.items():
        print(f"\nTanker {t}")
        for step in trips:
            print(step)

    print("\n================ SUMMARY ================")
    print("Total Cost (Rs Cr):", round(cost, 2))
    print("Remaining Demand:", remaining)
