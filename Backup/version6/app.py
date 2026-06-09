import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="HPCL Tanker Optimization", page_icon="🚢", layout="wide")

# ---------------------- DATA INITIATION ----------------------

@st.cache_data
def get_default_data():
    tankers = pd.DataFrame({
        "Tanker": [f"T{i}" for i in range(1, 10)],
        "Capacity": [50000]*7 + [25000]*2,
        "Hire Rate": [0.63, 0.49, 0.51, 0.51, 0.53, 0.57, 0.65, 0.39, 0.38]
    })

    demand = pd.DataFrame({
        "Unloading Port": [f"U{i}" for i in range(1, 12)],
        "Demand": [40000,135000,5000,20000,20000,20000,110000,30000,20000,20000,20000]
    })

    lu_data = {
        "L1":{"U1":0.4,"U2":0.7,"U3":0.4,"U4":0.4,"U5":0.4,"U6":0.6,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.7},
        "L2":{"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.5,"U11":0.6},
        "L3":{"U1":0.4,"U2":0.6,"U3":0.5,"U4":0.4,"U5":0.4,"U6":0.5,"U7":0.5,"U8":0.5,"U9":0.3,"U10":0.6,"U11":0.6},
        "L4":{"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.6},
        "L5":{"U1":0.4,"U2":0.6,"U3":0.4,"U4":0.3,"U5":0.3,"U6":0.5,"U7":0.5,"U8":0.4,"U9":0.3,"U10":0.5,"U11":0.5},
        "L6":{"U1":0.58,"U2":0.73,"U3":0.64,"U4":0.56,"U5":0.56,"U6":0.65,"U7":0.67,"U8":0.64,"U9":0.50,"U10":0.70,"U11":0.73}
    }
    trip_LU = pd.DataFrame(lu_data).T.reset_index().rename(columns={"index": "Loading Port"})

    uu_data = {
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
    trip_UU = pd.DataFrame(uu_data).T.reset_index().rename(columns={"index": "Unloading Port 1"})

    return tankers, demand, trip_LU, trip_UU


if "tankers" not in st.session_state:
    t, d, lu, uu = get_default_data()
    st.session_state.tankers = t
    st.session_state.demand = d
    st.session_state.trip_LU = lu
    st.session_state.trip_UU = uu


def prepare_optimization_input(max_days):
    tankers_df = st.session_state.tankers
    demand_df = st.session_state.demand
    lu_df = st.session_state.trip_LU
    uu_df = st.session_state.trip_UU

    tanker_capacity = {str(row["Tanker"]): float(row["Capacity"]) for _, row in tankers_df.iterrows()}
    tanker_hire_rate = {str(row["Tanker"]): float(row["Hire Rate"]) for _, row in tankers_df.iterrows()}
    demand = {str(row["Unloading Port"]): float(row["Demand"]) for _, row in demand_df.iterrows()}

    trip_time_LU = {}
    for _, row in lu_df.iterrows():
        l = str(row["Loading Port"])
        trip_time_LU[l] = {col: float(row[col]) for col in lu_df.columns if col != "Loading Port"}

    trip_time_UU = {}
    for _, row in uu_df.iterrows():
        u = str(row["Unloading Port 1"])
        trip_time_UU[u] = {col: float(row[col]) for col in uu_df.columns if col != "Unloading Port 1"}

    return {
        "loading_ports": list(trip_time_LU.keys()),
        "unloading_ports": list(demand.keys()),
        "tanker_capacity": tanker_capacity,
        "tanker_hire_rate": tanker_hire_rate,
        "demand": demand,
        "trip_time_LU": trip_time_LU,
        "trip_time_UU": trip_time_UU,
        "max_days": float(max_days)
    }


def optimize(data):
    prob = pulp.LpProblem("HPCL_Optimization", pulp.LpMinimize)

    single_routes, double_routes = [], []

    for l in data["loading_ports"]:
        for u1 in data["unloading_ports"]:

            if u1 in data["trip_time_LU"][l]:

                return_time = min(
                    data["trip_time_LU"][l2][u1]
                    for l2 in data["loading_ports"]
                    if u1 in data["trip_time_LU"][l2]
                )

                single_routes.append((l, u1, data["trip_time_LU"][l][u1] + return_time))

            if u1 in data["trip_time_UU"]:
                for u2 in data["unloading_ports"]:
                    if u1 != u2 and u2 in data["trip_time_UU"][u1]:

                        return_time = min(
                            data["trip_time_LU"][l2][u2]
                            for l2 in data["loading_ports"]
                            if u2 in data["trip_time_LU"][l2]
                        )

                        rt = data["trip_time_LU"][l][u1] + data["trip_time_UU"][u1][u2] + return_time
                        double_routes.append((l, u1, u2, rt))

    y_single, y_double = {}, {}
    cargo_single, cargo_d1, cargo_d2 = {}, {}, {}

    for t in data["tanker_capacity"]:
        for (l,u1,_) in single_routes:
            y_single[(t,l,u1)] = pulp.LpVariable(f"y_{t}_{l}_{u1}",0,cat="Integer")
            cargo_single[(t,l,u1)] = pulp.LpVariable(f"c_{t}_{l}_{u1}",0)

        for (l,u1,u2,_) in double_routes:
            y_double[(t,l,u1,u2)] = pulp.LpVariable(f"y_{t}_{l}_{u1}_{u2}",0,cat="Integer")
            cargo_d1[(t,l,u1,u2)] = pulp.LpVariable(f"c1_{t}_{l}_{u1}_{u2}",0)
            cargo_d2[(t,l,u1,u2)] = pulp.LpVariable(f"c2_{t}_{l}_{u1}_{u2}",0)

    single_time = {(l,u1):rt for l,u1,rt in single_routes}
    double_time = {(l,u1,u2):rt for l,u1,u2,rt in double_routes}

    prob += (
        pulp.lpSum(data["tanker_hire_rate"][t]*single_time[(l,u1)]*y_single[(t,l,u1)] for (t,l,u1) in y_single)
        +
        pulp.lpSum(data["tanker_hire_rate"][t]*double_time[(l,u1,u2)]*y_double[(t,l,u1,u2)] for (t,l,u1,u2) in y_double)
    )

    for u in data["unloading_ports"]:
        prob += (
            pulp.lpSum(cargo_single[(t,l,u1)] for (t,l,u1) in cargo_single if u1==u)
            +
            pulp.lpSum(cargo_d1[(t,l,u1,u2)] for (t,l,u1,u2) in cargo_d1 if u1==u)
            +
            pulp.lpSum(cargo_d2[(t,l,u1,u2)] for (t,l,u1,u2) in cargo_d2 if u2==u)
            >= data["demand"][u]
        )

    for (t,l,u1) in y_single:
        prob += cargo_single[(t,l,u1)] <= data["tanker_capacity"][t]*y_single[(t,l,u1)]

    for (t,l,u1,u2) in y_double:
        prob += cargo_d1[(t,l,u1,u2)] + cargo_d2[(t,l,u1,u2)] <= data["tanker_capacity"][t]*y_double[(t,l,u1,u2)]

    for t in data["tanker_capacity"]:
        prob += (
            pulp.lpSum(single_time[(l,u1)]*y_single[(t,l,u1)] for (tt,l,u1) in y_single if tt==t)
            +
            pulp.lpSum(double_time[(l,u1,u2)]*y_double[(t,l,u1,u2)] for (tt,l,u1,u2) in y_double if tt==t)
            <= data["max_days"]
        )

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    rows=[]
    for (t,l,u1),v in y_single.items():
        if v.varValue>0:
            rows.append([t,l,u1,"-",int(v.varValue),pulp.value(cargo_single[(t,l,u1)]),0,single_time[(l,u1)]])

    for (t,l,u1,u2),v in y_double.items():
        if v.varValue>0:
            rows.append([t,l,u1,u2,int(v.varValue),
                         pulp.value(cargo_d1[(t,l,u1,u2)]),
                         pulp.value(cargo_d2[(t,l,u1,u2)]),
                         double_time[(l,u1,u2)]])

    df = pd.DataFrame(rows,columns=["Tanker","Loading Port","Unload Port 1","Unload Port 2","Trips","Cargo U1","Cargo U2","Route Time"])
    return pulp.value(prob.objective), df