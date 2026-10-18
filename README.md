# Coastal Vessel Optimization

### Maritime Logistics Optimization using Integer Linear Programming and Streamlit

A decision-support system developed for the HP Power Lab 2.0 Challenge (Hindustan Petroleum Corporation Limited) that optimizes coastal tanker allocation for bulk liquid cargo transportation. The system minimizes total maritime transportation costs by determining optimal tanker assignments, voyage routes, and cargo allocations while satisfying strict industrial operational constraints.

The solution combines Mixed Integer Linear Programming (MILP) powered by PuLP and the COIN-OR CBC Solver with an interactive Streamlit dashboard. Logistics planners can modify tanker fleet details, port demands, and voyage duration matrices before executing mathematical optimization to generate cost-efficient voyage schedules.

---

## Overview

Efficient coastal shipping is critical for minimizing supply chain operational costs in bulk petroleum and liquid cargo transportation. Along the Indian coastline, coastal refineries produce refined petroleum products that must be transported to coastal consumption depots and terminal ports. 

This project formulates the coastal tanker allocation and voyage scheduling problem as a Mixed Integer Linear Programming (MILP) model where:

- A dedicated fleet of coastal tankers transports liquid bulk cargo
- Each tanker voyage loads cargo from exactly one designated loading port (refinery terminal)
- Each voyage serves either a single discharge port or up to two discharge ports (split discharge)
- Demand at every destination terminal must be satisfied
- Vessel monthly operational availability limits are strictly respected
- Vessel cargo payload capacity cannot be exceeded
- Total fleet charter hire transportation expenditure is minimized

The optimization engine computes the optimal assignment of tankers to routes, the exact number of trips per route, and the specific tonnage delivered to each destination port.

---

## Features

- Mixed Integer Linear Programming Optimization: Mathematical formulation utilizing PuLP and COIN-OR CBC solver for optimal fleet assignment.
- Interactive Web Dashboard: Real-time user interface built with Streamlit for logistics dispatchers and supply chain planners.
- Editable Fleet and Demand Data: Dynamic in-browser data grids supporting direct cell editing, Excel copy-paste (Ctrl+V), and CSV upload/download.
- Dual Discharge Optimization: Supports both single-port discharge voyages and two-port split cargo discharge itineraries.
- Operational Availability Limits: Enforces maximum monthly operating days (30-day default) per vessel to prevent fleet overutilization.
- Cargo Payload Integrity: Accurately couples cargo delivery variables with vessel deadweight capacity and trip counts.
- Turn-by-Turn Mission Logs: Generates clear, human-readable voyage instructions for every active vessel in the fleet.
- Comprehensive Visual Analytics: Interactive bar charts for fleet utilization and loading port throughput, route breakdown metrics, and top route rankings.
- One-Click Schedule Export: Download complete optimized voyage schedules directly as CSV files for operational deployment.

---

## System Architecture

```text
Input Data
│
├── Tankers
├── Capacities
├── Hire Rates
├── Port Demands
├── Loading → Unloading Trip Times
└── Unloading → Unloading Trip Times
│
▼
Data Preparation
│
▼
Integer Linear Programming
(PuLP Solver)
│
├── Decision Variables
├── Objective Function
├── Demand Constraints
├── Capacity Constraints
└── Working-Day Constraints
│
▼
Optimal Tanker Schedule
│
▼
Streamlit Dashboard
```

---

## Optimization Workflow

```text
Fleet Information
        │
        ▼
Demand Data
        │
        ▼
Trip Time Matrices
        │
        ▼
ILP Model Construction
        │
        ▼
PuLP Optimization
        │
        ▼
Optimal Tanker Assignment
        │
        ▼
Transportation Cost Analysis
```

---

## Mathematical Optimization Model

The optimization engine models the maritime transportation problem using decision variables representing voyage trips and cargo volumes.

### Sets and Indices

- T: Set of available coastal tankers {T1, T2, T3, T4, T5, T6, T7, T8, T9}
- L: Set of refinery loading ports {L1, L2, L3, L4, L5, L6}
- U: Set of destination unloading ports {U1, U2, U3, U4, U5, U6, U7, U8, U9, U10, U11}

### Model Parameters

- Capacity[t]: Cargo carrying capacity of tanker t in metric tonnes (MT)
- HireRate[t]: Daily charter hire rate of tanker t (in Crores per day)
- Demand[u]: Monthly product demand at destination port u in metric tonnes (MT)
- TripTime_LU[l][u1]: Transit and port operation duration in days from loading port l to unloading port u1
- TripTime_UU[u1][u2]: Inter-port transit duration in days between first unloading port u1 and second unloading port u2
- MaxDays: Maximum operational days available per tanker within the planning period (default 30.0 days)

### Decision Variables

- y[t, l, u1, None]: Non-negative integer variable representing the number of single-port trips made by tanker t from loading port l to unloading port u1.
- y[t, l, u1, u2]: Non-negative integer variable representing the number of two-port split trips made by tanker t from loading port l to unloading port u1 and then unloading port u2 (where u1 != u2).
- x[t, l, u1, None, u1]: Non-negative continuous variable representing cargo volume (MT) delivered to unloading port u1 on single-port trips.
- x[t, l, u1, u2, u1]: Non-negative continuous variable representing cargo volume (MT) delivered to first unloading port u1 on two-port trips.
- x[t, l, u1, u2, u2]: Non-negative continuous variable representing cargo volume (MT) delivered to second unloading port u2 on two-port trips.

---

## Objective Function

The objective is to minimize total fleet charter hire transportation cost across the entire monthly planning horizon:

```text
Trip Cost = Hire Rate × Voyage Time
```

Mathematically, the total cost represents the sum of charter hire costs across all single-port and two-port voyages:

Total Cost = Sum over all valid routes (t, l, u1, u2) of:
HireRate[t] × (TripTime_LU[l][u1] + TripTime_UU[u1][u2]) × y[t, l, u1, u2]

Where TripTime_UU is 0 for single-port discharge voyages.

---

## Operational Constraints

### 1. Demand Satisfaction Constraint

Every unloading port must receive cargo equal to or greater than its required monthly demand. Cargo delivered across all single-stop and two-stop voyages serving port u must satisfy:

Sum over all trips delivering to port u of x[t, l, u1, u2, u] >= Demand[u]

This ensures zero fuel deficit across coastal consumer depots.

### 2. Vessel Carrying Capacity Constraint

For every specific route itinerary assigned to a vessel, the total cargo delivered across the destination ports cannot exceed the physical carrying capacity of the vessel multiplied by the number of trips performed on that route:

For single-port voyages:
x[t, l, u1, None, u1] <= Capacity[t] × y[t, l, u1, None]

For two-port split discharge voyages:
x[t, l, u1, u2, u1] + x[t, l, u1, u2, u2] <= Capacity[t] × y[t, l, u1, u2]

This formulation allows optimal flexible cargo splitting between u1 and u2 on dual-discharge voyages while strictly respecting tanker payload limits.

### 3. Tanker Monthly Working Limit

Each vessel has an operational upper bound on cumulative operating days within the calendar month (accounting for weather, maintenance, and bunkering buffers). The cumulative voyage duration across all assignments for tanker t must satisfy:

Sum over all routes served by tanker t of:
(TripTime_LU[l][u1] + TripTime_UU[u1][u2]) × y[t, l, u1, u2] <= MaxDays

The default threshold is 30.0 days per tanker.

### 4. Single Loading Port Rule

Each voyage loads bulk liquid cargo from exactly one refinery loading port l. Multi-load itineraries are prohibited to maintain refinery scheduling simplicity and product batch integrity.

### 5. Maximum Two Discharge Ports Rule

A vessel can discharge its cargo either completely at a single unloading port u1 or across a sequence of two unloading ports (u1 followed by u2). Discharging across three or more ports is excluded to control turnaround delays, demurrage, and coastal transit risks.

---

## Baseline Dataset Specification

The default industrial scenario provided in the HP Power Lab 2.0 challenge comprises 9 coastal vessels, 6 loading ports, and 11 unloading terminals.

### Tanker Fleet Specifications

| Tanker ID | Deadweight Capacity (MT) | Daily Charter Hire Rate (₹ Cr/day) | Vessel Class |
|-----------|--------------------------|-------------------------------------|--------------|
| T1 | 50,000 | 0.63 | Medium Range (MR) |
| T2 | 50,000 | 0.49 | Medium Range (MR) |
| T3 | 50,000 | 0.51 | Medium Range (MR) |
| T4 | 50,000 | 0.51 | Medium Range (MR) |
| T5 | 50,000 | 0.53 | Medium Range (MR) |
| T6 | 50,000 | 0.57 | Medium Range (MR) |
| T7 | 50,000 | 0.65 | Medium Range (MR) |
| T8 | 25,000 | 0.39 | General Purpose (GP) |
| T9 | 25,000 | 0.38 | General Purpose (GP) |

- Total Fleet Single-Lift Capacity: 400,000 MT
- Large Tankers (50,000 MT): 7 Vessels (T1 through T7)
- Small Tankers (25,000 MT): 2 Vessels (T8 and T9)

### Destination Port Demands

| Unloading Port | Monthly Demand (MT) | Coastal Destination Profile |
|----------------|---------------------|-----------------------------|
| U1 | 40,000 | High-demand coastal hub |
| U2 | 135,000 | Primary major terminal |
| U3 | 5,000 | Low-demand feeder depot |
| U4 | 20,000 | Standard regional depot |
| U5 | 20,000 | Standard regional depot |
| U6 | 20,000 | Standard regional depot |
| U7 | 110,000 | Major coastal consumption center |
| U8 | 30,000 | Medium coastal terminal |
| U9 | 20,000 | Standard regional depot |
| U10 | 20,000 | Standard regional depot |
| U11 | 20,000 | Standard regional depot |

- Cumulative Monthly Demand: 440,000 MT across all 11 discharge terminals.

### Transit Duration Matrices

- Loading to Unloading (LU Matrix): Captures round-trip or outward laden transit durations (0.30 to 0.73 days) across 6 loading ports and 11 unloading ports.
- Unloading to Unloading (UU Matrix): Captures inter-port coastal transit times (0.05 to 0.40 days) for dual-discharge voyages.

---

## Streamlit Interactive Dashboard

The web interface is organized into intuitive, functional modules:

### 1. Sidebar Control Panel
- Maximum Days Available: Adjustable numerical input (default: 30.0 days) allowing users to simulate scenarios with tighter operational windows (e.g. 20-day maintenance schedules or 25-day bad weather buffers).
- Optimization Trigger: Primary action button executing the mathematical model.
- Fleet and Port Data Summary: Instant counts of loaded refineries, discharge ports, and active fleet vessels.

### 2. Data Management Console
- In-browser interactive editable tables for Tankers, Demands, and Trip Duration Matrices.
- Excel copy and paste support directly into table cells.
- CSV file uploader for uploading custom enterprise datasets.
- Built-in data downloading to save configured parameters locally.

### 3. Executive KPI Metric Cards
- Total Transportation Cost (displayed in ₹ Crores).
- Total Routes Taken (number of distinct route legs scheduled).
- Total Trips Made (cumulative voyage count across all vessels).
- Active Tankers Used (number of vessels utilized out of the 9 available).

### 4. Analytical Tabs
- Tab 1: Deployment Overview:
  - Interactive bar chart of trips completed per tanker.
  - Interactive bar chart of trips originating from each loading port.
  - Tanker Mission Log: Turn-by-turn expandable voyage logs displaying loading port, discharge port sequence, and repeat voyage counts for each vessel.
- Tab 2: Detailed Schedule:
  - Complete schedule table showing Tanker, Loading Port, Unload Port 1, Unload Port 2, Trips, Cargo delivered to U1, and Cargo delivered to U2.
  - CSV export button downloading hpcl_tanker_schedule.csv.
- Tab 3: Analytics and Route Insights:
  - Single-stop versus two-stop route breakdown metrics.
  - Top 5 most frequently utilized coastal routes table.

---

## Technologies Used

| Category | Technology | Purpose |
|----------|------------|---------|
| Programming Language | Python 3 | Core application and model logic |
| Mathematical Modeling | PuLP | Mixed Integer Linear Programming (MILP) formulation |
| Optimization Solver | COIN-OR CBC | Branch-and-cut linear programming solver |
| Web Application | Streamlit | Interactive user interface and data visualization |
| Data Processing | Pandas | DataFrames, tabular calculations, and matrix operations |
| Numerical Computing | NumPy | Array manipulations and numerical evaluations |

---

## Project Structure

```text
HPCL-Coastal-Vessel-Optimization/
│
├── app.py
├── HP.py
├── Architecture.md
├── Backup/
│   ├── version1/
│   ├── version2/
│   ├── version3/
│   ├── version4/
│   ├── version5/
│   └── version6/
└── README.md
```

### File Manifest

- app.py: Complete Streamlit web application integrating the UI, parameter managers, MILP optimization engine, and visual analytics.
- HP.py: Standalone command-line optimization script containing the default baseline data instance and direct PuLP model execution.
- Architecture.md: Detailed technical documentation covering system architecture, mathematical derivations, component interactions, and data schemas.
- Backup/: Historical codebase iterations (versions 1 through 6) documenting the evolutionary development and constraint refinements.
- README.md: Comprehensive project overview, user manual, and problem specification.

---

## Installation

Ensure Python 3.8 or higher is installed on your system.

Clone the project repository:

```bash
git clone https://github.com/kajaredhruv433/kajaredhruv433-Coastal-Vessel-Optimization-HP-Power-Lab-2.0-.git
cd kajaredhruv433-Coastal-Vessel-Optimization-HP-Power-Lab-2.0-
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Requirements

The core dependencies required to run the project are:

```text
streamlit
pandas
numpy
pulp
```

---

## Running the Application

### 1. Launch the Interactive Web Dashboard

To run the Streamlit application:

```bash
streamlit run app.py
```

The application will open automatically in your default web browser at http://localhost:8501.

### 2. Run the Standalone Optimization Script

To execute the solver directly from the terminal without launching the web browser:

```bash
python HP.py
```

This will solve the baseline instance and output the minimum achievable cost alongside the optimal trip schedule in the console.

---

## Optimization Output

The optimization engine outputs a complete operational plan detailing:

- Vessel Assignments: Specific tanker allocated to each voyage.
- Origin Refinery: Designated loading port for each voyage.
- Destination Terminals: Primary discharge port and optional secondary discharge port.
- Trip Frequencies: Number of repeated voyages per route leg.
- Cargo Volume Allocations: Metric tonnes delivered to each discharge terminal per trip.
- Total Financial Cost: Cumulative fleet charter expenditure in ₹ Crores.
- Fleet Utilization Profile: Operational days and trip counts per vessel.

---

## Industrial Applications

- Coastal Petroleum Tanker Scheduling: Optimizing coastal vessel chartering for oil marketing companies (OMCs).
- Bulk Liquid Chemical Transportation: Route optimization for industrial chemical fleets.
- Multi-Port Maritime Logistics: Scheduling coastal feeder networks with co-loading and multi-drop delivery.
- Charter Fleet Sizing and Selection: Evaluating cost trade-offs between long-term charter vessels and spot market tankers.
- Supply Chain Decision Support: Scenario analysis for refinery shutdown, port maintenance, and seasonal demand surges.

---

## Future Improvements

- Multi-Objective Optimization: Jointly minimizing monetary charter hire cost and greenhouse gas (GHG) carbon emissions.
- Weather and Tidal Routing: Incorporating dynamic maritime weather conditions, wave heights, and tidal draft restrictions.
- Port Congestion and Demurrage Modeling: Accounting for queueing delays and berth waiting times at major discharge ports.
- Return Ballast Leg Optimization: Explicitly modeling return ballast voyages from unloading terminals back to loading refineries.
- Live AIS Vessel Tracking: Integration with Automatic Identification System (AIS) maritime data feeds for real-time fleet tracking.
- Multi-Period Planning: Extending the single-period monthly model to rolling-horizon multi-period inventory-routing formulations.

---

## Key Learnings

- Mixed Integer Linear Programming (MILP) formulation for maritime supply chains.
- Operations Research techniques for vessel fleet allocation and route scheduling.
- Constraint satisfaction for complex multi-drop discharge logistics.
- Coupling continuous cargo allocation variables with discrete vessel trip counts.
- Building interactive decision-support tools using Streamlit and Pandas.
- Translating real-world maritime operating parameters into mathematical optimization models.

---

## Authors and Acknowledgments

### Lead Developer
- Dhruv Mahendra Kajare

### Team Members
- Juhi Nale
- Neha Tarmale

### Acknowledgments
Developed as part of the HP Power Lab 2.0 Challenge organized by Hindustan Petroleum Corporation Limited (HPCL). This project demonstrates the application of Integer Linear Programming and operations research to resolve complex maritime logistics challenges, optimize coastal tanker scheduling, and minimize bulk transportation expenditure.
