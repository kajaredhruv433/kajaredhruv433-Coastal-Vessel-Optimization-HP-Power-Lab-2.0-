import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="HPCL Tanker Optimization", page_icon="", layout="wide")


# ---------------------- DATA INITIATION ----------------------

@st.cache_data
def get_default_data():
    tankers = pd.DataFrame({
        "Tanker": [f"T{i}" for i in range(1, 10)],
        "Capacity": [50000] * 7 + [25000] * 2,
        "Hire Rate": [0.63, 0.49, 0.51, 0.51, 0.53, 0.57, 0.65, 0.39, 0.38]
    })

    demand = pd.DataFrame({
        "Unloading Port": [f"U{i}" for i in range(1, 12)],
        "Demand": [40000, 135000, 5000, 20000, 20000, 20000, 110000, 30000, 20000, 20000, 20000]
    })

    lu_data = {
        "L1": {"U1": 0.4, "U2": 0.7, "U3": 0.4, "U4": 0.4, "U5": 0.4, "U6": 0.6, "U7": 0.5, "U8": 0.4, "U9": 0.3,
               "U10": 0.5, "U11": 0.7},
        "L2": {"U1": 0.4, "U2": 0.6, "U3": 0.5, "U4": 0.4, "U5": 0.4, "U6": 0.5, "U7": 0.5, "U8": 0.5, "U9": 0.3,
               "U10": 0.5, "U11": 0.6},
        "L3": {"U1": 0.4, "U2": 0.6, "U3": 0.5, "U4": 0.4, "U5": 0.4, "U6": 0.5, "U7": 0.5, "U8": 0.5, "U9": 0.3,
               "U10": 0.6, "U11": 0.6},
        "L4": {"U1": 0.4, "U2": 0.6, "U3": 0.4, "U4": 0.3, "U5": 0.3, "U6": 0.5, "U7": 0.5, "U8": 0.4, "U9": 0.3,
               "U10": 0.5, "U11": 0.6},
        "L5": {"U1": 0.4, "U2": 0.6, "U3": 0.4, "U4": 0.3, "U5": 0.3, "U6": 0.5, "U7": 0.5, "U8": 0.4, "U9": 0.3,
               "U10": 0.5, "U11": 0.5},
        "L6": {"U1": 0.58, "U2": 0.73, "U3": 0.64, "U4": 0.56, "U5": 0.56, "U6": 0.65, "U7": 0.67, "U8": 0.64,
               "U9": 0.50, "U10": 0.70, "U11": 0.73}
    }
    trip_LU = pd.DataFrame(lu_data).T.reset_index().rename(columns={"index": "Loading Port"})

    uu_data = {
        "U1": {"U2": 0.35, "U3": 0.19, "U4": 0.16, "U5": 0.16, "U6": 0.25, "U7": 0.23, "U8": 0.19, "U9": 0.09,
               "U10": 0.19, "U11": 0.33},
        "U2": {"U1": 0.36, "U3": 0.38, "U4": 0.37, "U5": 0.37, "U6": 0.15, "U7": 0.34, "U8": 0.38, "U9": 0.29,
               "U10": 0.40, "U11": 0.19},
        "U3": {"U1": 0.16, "U2": 0.33, "U4": 0.16, "U5": 0.16, "U6": 0.25, "U7": 0.21, "U8": 0.17, "U9": 0.09,
               "U10": 0.19, "U11": 0.32},
        "U4": {"U1": 0.18, "U2": 0.37, "U3": 0.21, "U5": 0.12, "U6": 0.29, "U7": 0.25, "U8": 0.21, "U9": 0.05,
               "U10": 0.21, "U11": 0.35},
        "U5": {"U1": 0.18, "U2": 0.37, "U3": 0.21, "U4": 0.12, "U6": 0.29, "U7": 0.25, "U8": 0.21, "U9": 0.05,
               "U10": 0.21, "U11": 0.35},
        "U6": {"U1": 0.29, "U2": 0.17, "U3": 0.32, "U4": 0.31, "U5": 0.31, "U7": 0.22, "U8": 0.32, "U9": 0.24,
               "U10": 0.34, "U11": 0.18},
        "U7": {"U1": 0.19, "U2": 0.29, "U3": 0.21, "U4": 0.20, "U5": 0.20, "U6": 0.15, "U8": 0.21, "U9": 0.12,
               "U10": 0.21, "U11": 0.28},
        "U8": {"U1": 0.16, "U2": 0.33, "U3": 0.17, "U4": 0.16, "U5": 0.16, "U6": 0.25, "U7": 0.21, "U9": 0.09,
               "U10": 0.19, "U11": 0.32},
        "U9": {"U1": 0.17, "U2": 0.37, "U3": 0.21, "U4": 0.12, "U5": 0.12, "U6": 0.29, "U7": 0.25, "U8": 0.21,
               "U10": 0.21, "U11": 0.35},
        "U10": {"U1": 0.14, "U2": 0.34, "U3": 0.18, "U4": 0.15, "U5": 0.15, "U6": 0.27, "U7": 0.20, "U8": 0.18,
                "U9": 0.07, "U11": 0.33},
        "U11": {"U1": 0.33, "U2": 0.17, "U3": 0.34, "U4": 0.33, "U5": 0.33, "U6": 0.13, "U7": 0.30, "U8": 0.34,
                "U9": 0.25, "U10": 0.36}
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
        l_port = str(row["Loading Port"])
        trip_time_LU[l_port] = {}
        for col in lu_df.columns:
            if col != "Loading Port" and pd.notna(row[col]):
                trip_time_LU[l_port][col] = float(row[col])

    trip_time_UU = {}
    for _, row in uu_df.iterrows():
        u1_port = str(row["Unloading Port 1"])
        trip_time_UU[u1_port] = {}
        for col in uu_df.columns:
            if col != "Unloading Port 1" and pd.notna(row[col]):
                trip_time_UU[u1_port][col] = float(row[col])

    # approximate symmetric return times U -> L using L -> U table
    trip_time_UL = {}
    for u in demand.keys():
        trip_time_UL[u] = {}
        for l in trip_time_LU.keys():
            if u in trip_time_LU[l]:
                trip_time_UL[u][l] = trip_time_LU[l][u]

    return {
        "loading_ports": list(trip_time_LU.keys()),
        "unloading_ports": list(demand.keys()),
        "tanker_capacity": tanker_capacity,
        "tanker_hire_rate": tanker_hire_rate,
        "demand": demand,
        "trip_time_LU": trip_time_LU,
        "trip_time_UU": trip_time_UU,
        "trip_time_UL": trip_time_UL,
        "max_days": float(max_days)
    }


# ---------------------- OPTIMIZATION ----------------------

def optimize(data):
    prob = pulp.LpProblem("HPCL_Optimization", pulp.LpMinimize)

    # Build only valid routes once
    single_routes = []
    double_routes = []

    for l in data["loading_ports"]:
        for u1 in data["unloading_ports"]:
            if u1 in data["trip_time_LU"].get(l, {}) and l in data["trip_time_UL"].get(u1, {}):
                route_time = data["trip_time_LU"][l][u1] + data["trip_time_UL"][u1][l]
                single_routes.append((l, u1, route_time))

            if u1 in data["trip_time_UU"]:
                for u2 in data["unloading_ports"]:
                    if u1 != u2:
                        if (
                                u1 in data["trip_time_LU"].get(l, {})
                                and u2 in data["trip_time_UU"].get(u1, {})
                                and l in data["trip_time_UL"].get(u2, {})
                        ):
                            route_time = (
                                    data["trip_time_LU"][l][u1]
                                    + data["trip_time_UU"][u1][u2]
                                    + data["trip_time_UL"][u2][l]
                            )
                            double_routes.append((l, u1, u2, route_time))

    y_single = {}
    y_double = {}
    cargo_single = {}
    cargo_double_1 = {}
    cargo_double_2 = {}

    # Variables
    for t in data["tanker_capacity"]:
        for (l, u1, _) in single_routes:
            y_single[(t, l, u1)] = pulp.LpVariable(f"y_{t}_{l}_{u1}", lowBound=0, cat="Integer")
            cargo_single[(t, l, u1)] = pulp.LpVariable(f"cargo_{t}_{l}_{u1}", lowBound=0)

        for (l, u1, u2, _) in double_routes:
            y_double[(t, l, u1, u2)] = pulp.LpVariable(f"y_{t}_{l}_{u1}_{u2}", lowBound=0, cat="Integer")
            cargo_double_1[(t, l, u1, u2)] = pulp.LpVariable(f"cargo1_{t}_{l}_{u1}_{u2}", lowBound=0)
            cargo_double_2[(t, l, u1, u2)] = pulp.LpVariable(f"cargo2_{t}_{l}_{u1}_{u2}", lowBound=0)

    single_time = {(l, u1): rt for (l, u1, rt) in single_routes}
    double_time = {(l, u1, u2): rt for (l, u1, u2, rt) in double_routes}

    # Objective
    prob += (
            pulp.lpSum(
                data["tanker_hire_rate"][t] * single_time[(l, u1)] * y_single[(t, l, u1)]
                for (t, l, u1) in y_single
            )
            +
            pulp.lpSum(
                data["tanker_hire_rate"][t] * double_time[(l, u1, u2)] * y_double[(t, l, u1, u2)]
                for (t, l, u1, u2) in y_double
            )
    )

    # Demand constraints using actual cargo
    for u in data["unloading_ports"]:
        prob += (
                pulp.lpSum(
                    cargo_single[(t, l, u1)]
                    for (t, l, u1) in cargo_single if u1 == u
                )
                +
                pulp.lpSum(
                    cargo_double_1[(t, l, u1, u2)]
                    for (t, l, u1, u2) in cargo_double_1 if u1 == u
                )
                +
                pulp.lpSum(
                    cargo_double_2[(t, l, u1, u2)]
                    for (t, l, u1, u2) in cargo_double_2 if u2 == u
                )
                >= data["demand"][u]
        )

    # Capacity constraints
    for (t, l, u1) in y_single:
        prob += cargo_single[(t, l, u1)] <= data["tanker_capacity"][t] * y_single[(t, l, u1)]

    for (t, l, u1, u2) in y_double:
        prob += (
                cargo_double_1[(t, l, u1, u2)] + cargo_double_2[(t, l, u1, u2)]
                <= data["tanker_capacity"][t] * y_double[(t, l, u1, u2)]
        )

    # Tanker max days
    for t in data["tanker_capacity"]:
        prob += (
                pulp.lpSum(
                    single_time[(l, u1)] * y_single[(t, l, u1)]
                    for (tt, l, u1) in y_single if tt == t
                )
                +
                pulp.lpSum(
                    double_time[(l, u1, u2)] * y_double[(t, l, u1, u2)]
                    for (tt, l, u1, u2) in y_double if tt == t
                )
                <= data["max_days"]
        )

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=30, gapRel=0.01)
    prob.solve(solver)

    if pulp.LpStatus[prob.status] not in ["Optimal", "Not Solved", "Integer Feasible", "Infeasible", "Undefined"]:
        return None, pd.DataFrame()

    if pulp.LpStatus[prob.status] == "Infeasible":
        return None, pd.DataFrame()

    results = []

    for (t, l, u1), var in y_single.items():
        if var.varValue and var.varValue > 0:
            results.append({
                "Tanker": t,
                "Loading Port": l,
                "Unload Port 1": u1,
                "Unload Port 2": "-",
                "Trips": int(round(var.varValue)),
                "Cargo U1": round(pulp.value(cargo_single[(t, l, u1)]), 2),
                "Cargo U2": 0.0,
                "Route Time (days)": round(single_time[(l, u1)], 3)
            })

    for (t, l, u1, u2), var in y_double.items():
        if var.varValue and var.varValue > 0:
            results.append({
                "Tanker": t,
                "Loading Port": l,
                "Unload Port 1": u1,
                "Unload Port 2": u2,
                "Trips": int(round(var.varValue)),
                "Cargo U1": round(pulp.value(cargo_double_1[(t, l, u1, u2)]), 2),
                "Cargo U2": round(pulp.value(cargo_double_2[(t, l, u1, u2)]), 2),
                "Route Time (days)": round(double_time[(l, u1, u2)], 3)
            })

    return pulp.value(prob.objective), pd.DataFrame(results)


# ---------------------- STREAMLIT UI ----------------------

with st.sidebar:
    st.title(" HPCL Optimizer")
    st.markdown("Run the optimization engine to minimize transportation costs.")

    st.markdown("### 🔧 Settings")
    max_days_input = st.number_input(
        "Maximum Days Available",
        min_value=1.0,
        value=30.0,
        step=1.0,
        help="Maximum operating days allowed per tanker"
    )

    st.divider()
    run_btn = st.button("🚀 Run Optimization", type="primary", use_container_width=True)

    st.divider()
    st.markdown("### Data Overview")
    st.markdown(f"- **Loading Ports**: {len(st.session_state.trip_LU)}")
    st.markdown(f"- **Unloading Ports**: {len(st.session_state.demand)}")
    st.markdown(f"- **Tankers Fleet**: {len(st.session_state.tankers)}")

st.title(" HPCL Tanker Scheduling Optimization")
st.markdown("### Intelligent Route Planning Dashboard")

with st.expander(" Manage Input Parameters & Data (Upload CSV / Edit Directly)", expanded=False):
    st.info(
        " You can directly double-click the tables below to edit them, paste data directly from Excel via `Ctrl+V`, or click the Download icon to get the CSV. **Alternatively, upload a CSV file directly.**")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.subheader("1. Tanker Fleet Details")
        up_tank = st.file_uploader("Upload Tanker CSV", type="csv", label_visibility="collapsed")
        if up_tank:
            st.session_state.tankers = pd.read_csv(up_tank)
        st.session_state.tankers = st.data_editor(st.session_state.tankers, num_rows="dynamic",
                                                  use_container_width=True, key="edit_tankers")

        st.subheader("2. Port Demands")
        up_dem = st.file_uploader("Upload Demand CSV", type="csv", label_visibility="collapsed")
        if up_dem:
            st.session_state.demand = pd.read_csv(up_dem)
        st.session_state.demand = st.data_editor(st.session_state.demand, num_rows="dynamic", use_container_width=True,
                                                 key="edit_demand")

    with col_d2:
        st.subheader("3. Loading to Unloading Trip Time")
        up_lu = st.file_uploader("Upload LU Trip Time CSV", type="csv", label_visibility="collapsed")
        if up_lu:
            st.session_state.trip_LU = pd.read_csv(up_lu)
        st.session_state.trip_LU = st.data_editor(st.session_state.trip_LU, num_rows="dynamic",
                                                  use_container_width=True, key="edit_lu")

        st.subheader("4. Unloading to Unloading Trip Time")
        up_uu = st.file_uploader("Upload UU Trip Time CSV", type="csv", label_visibility="collapsed")
        if up_uu:
            st.session_state.trip_UU = pd.read_csv(up_uu)
        st.session_state.trip_UU = st.data_editor(st.session_state.trip_UU, num_rows="dynamic",
                                                  use_container_width=True, key="edit_uu")

st.divider()

if run_btn:
    with st.spinner("Executing mathematical optimization model..."):
        opt_data = prepare_optimization_input(max_days_input)
        cost, df = optimize(opt_data)

    if cost is None or len(df) == 0:
        st.error(" Problem is Infeasible. Demand could not be met under the given restriction with the given fleet.")
    else:
        st.success(" Optimization completed successfully!")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Cost", value=f"₹ {cost:,.4f} Cr")
        with col2:
            st.metric(label="Total Routes Taken", value=len(df))
        with col3:
            st.metric(label="Total Trips Made", value=int(df["Trips"].sum()))
        with col4:
            st.metric(label="Active Tankers Used", value=df["Tanker"].nunique())

        st.divider()

        tab1, tab2, tab3 = st.tabs([" Deployment Overview", " Detailed Schedule", " Analytics & Insights"])

        with tab1:
            st.subheader("Fleet Utilization")
            col_bar1, col_bar2 = st.columns(2)
            with col_bar1:
                st.markdown("**Trips per Tanker**")
                tanker_summary = df.groupby("Tanker")["Trips"].sum().sort_values(ascending=False)
                st.bar_chart(tanker_summary)
            with col_bar2:
                st.markdown("**Trips by Loading Port**")
                load_summary = df.groupby("Loading Port")["Trips"].sum().sort_values(ascending=False)
                st.bar_chart(load_summary)

            st.markdown("---")
            st.subheader("Detailed Tanker Mission Log")
            st.markdown("Exact breakdown of operations performed by every individual Tanker in the fleet:")

            for active_tanker in sorted(df["Tanker"].unique()):
                tanker_jobs = df[df["Tanker"] == active_tanker]
                with st.expander(f" {active_tanker} Log  ({int(tanker_jobs['Trips'].sum())} total trips)",
                                 expanded=False):
                    for _, row in tanker_jobs.iterrows():
                        if row["Unload Port 2"] != "-":
                            st.markdown(
                                f"- Load at **{row['Loading Port']}** ➔ "
                                f"Unload **{row['Cargo U1']:.2f} MT** at **{row['Unload Port 1']}** ➔ "
                                f"Unload **{row['Cargo U2']:.2f} MT** at **{row['Unload Port 2']}** "
                                f"*(Repeated {row['Trips']} times, Route Time: {row['Route Time (days)']} days)*"
                            )
                        else:
                            st.markdown(
                                f"- Load at **{row['Loading Port']}** ➔ "
                                f"Unload **{row['Cargo U1']:.2f} MT** at **{row['Unload Port 1']}** "
                                f"*(Repeated {row['Trips']} times, Route Time: {row['Route Time (days)']} days)*"
                            )

        with tab2:
            st.subheader("Optimized Trip Schedule")
            st.dataframe(df.set_index("Tanker"), use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=" Download Schedule as CSV",
                data=csv,
                file_name='hpcl_tanker_schedule.csv',
                mime='text/csv',
            )

        with tab3:
            st.subheader("Route Analysis")
            multi_unload = df[df["Unload Port 2"] != "-"]
            single_unload = df[df["Unload Port 2"] == "-"]

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Single-Stop Routes", len(single_unload))
                st.markdown("Routes unloading entirely at one port.")
            with col_m2:
                st.metric("Multi-Stop Routes", len(multi_unload))
                st.markdown("Routes splitting load across two ports.")

            st.markdown("**Top 5 Most Frequent Routes**")
            top_routes = df.sort_values(by="Trips", ascending=False).head(5)
            st.dataframe(top_routes.set_index("Tanker"), use_container_width=True)

else:
    st.info(" Set your Max Days and click **Run Optimization** in the sidebar to generate the schedule.")
    st.markdown("### Ready to Optimize")
    st.markdown(
        "The system will formulate a Mixed Integer Linear Programming (MILP) model to determine the optimal assignment of tankers to loading and unloading ports based on the Input Parameters.")
    st.caption(
        "Developed for HPCL transportation logistics. Utilizes PuLP linear programming framework for finding optimal solutions.")