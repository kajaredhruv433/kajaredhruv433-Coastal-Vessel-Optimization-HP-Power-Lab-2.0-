import streamlit as st
import pandas as pd
import pulp

st.set_page_config(page_title="HPCL Tanker Optimization", page_icon="🚢", layout="wide")

# ---------------------- DATA ----------------------

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


# ---------------------- OPTIMIZATION ----------------------

def optimize():

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

    # Demand constraint
    for u in data["unloading_ports"]:
        prob += pulp.lpSum(
            data["tanker_capacity"][t] * y[(t,l,u1,u2)]
            for (t,l,u1,u2) in y if u1 == u or u2 == u
        ) >= data["demand"][u]

    # Tanker days constraint
    for t in data["tanker_capacity"]:
        prob += pulp.lpSum(
            (data["trip_time_LU"][l][u1] + (data["trip_time_UU"][u1][u2] if u2 else 0))
            * y[(t,l,u1,u2)]
            for (tt,l,u1,u2) in y if tt == t
        ) <= data["max_days"]

    prob.solve()

    results = []

    for k,v in y.items():
        if v.varValue and v.varValue > 0:
            t,l,u1,u2 = k
            results.append({
                "Tanker":t,
                "Loading Port":l,
                "Unload Port 1":u1,
                "Unload Port 2":u2 if u2 else "-",
                "Trips":int(v.varValue)
            })

    df = pd.DataFrame(results)

    return pulp.value(prob.objective), df


# ---------------------- STREAMLIT UI ----------------------

# Sidebar for controls
with st.sidebar:
    st.title("🚢 HPCL Optimizer")
    st.markdown("Run the optimization engine to minimize transportation costs while meeting demand across all ports.")
    run_btn = st.button("🚀 Run Optimization", type="primary", use_container_width=True)
    st.divider()
    st.markdown("### System Specs")
    st.markdown("- **Loading Ports**: 6")
    st.markdown("- **Unloading Ports**: 11")
    st.markdown("- **Tankers Fleet**: 9")
    
st.title("🚢 HPCL Tanker Scheduling Optimization")
st.markdown("### Intelligent Route Planning Dashboard")
st.divider()

if run_btn:
    with st.spinner("Executing mathematical optimization model..."):
        cost, df = optimize()
        
    st.success("✅ Optimization completed successfully!")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Cost", value=f"₹ {cost:,.2f}")
    with col2:
        st.metric(label="Total Routes Taken", value=len(df))
    with col3:
        st.metric(label="Total Trips Made", value=int(df["Trips"].sum()))
    with col4:
        st.metric(label="Active Tankers Used", value=df["Tanker"].nunique())
        
    st.divider()
    
    # Tabs for detailed views
    tab1, tab2, tab3 = st.tabs(["📊 Deployment Overview", "📅 Detailed Schedule", "📈 Analytics & Insights"])
    
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
            
    with tab2:
        st.subheader("Optimized Trip Schedule")
        
        # Displaying data nicely without index for cleaner look
        st.dataframe(df.set_index("Tanker"), use_container_width=True)
        
        # Download button for schedule
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Schedule as CSV",
            data=csv,
            file_name='hpcl_tanker_schedule.csv',
            mime='text/csv',
        )

    with tab3:
        st.subheader("Route Analysis")
        # Calculate some insights
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
    st.info("👈 Click **Run Optimization** in the sidebar to generate the schedule.")
    
    # Empty state visual
    st.markdown("### Ready to Optimize")
    st.markdown("The system will formulate a Mixed Integer Linear Programming (MILP) model to determine the optimal assignment of tankers to loading and unloading ports.")
    
    st.divider()
    st.caption("Developed for HPCL transportation logistics. Utilizes PuLP linear programming framework for finding optimal solutions.")