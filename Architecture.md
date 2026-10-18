# Coastal Vessel Optimization - Technical Architecture

### Architectural Specification and Mathematical Systems Design

This document details the software architecture, mathematical modeling framework, data pipelines, and design decisions behind the Coastal Vessel Optimization decision-support system, developed for the HP Power Lab 2.0 Challenge (Hindustan Petroleum Corporation Limited).

---

## Architectural Overview

The Coastal Vessel Optimization platform is designed as an interactive, data-driven operations research decision-support tool. It bridges advanced mathematical optimization with an intuitive web-based interface for maritime logistics planners and dispatchers.

The system is structured across four primary architectural tiers:

1. Presentation Tier: Built with Streamlit, providing reactive parameter controls, editable in-browser data grids, responsive KPI summaries, and analytical visualizations.
2. State and Data Management Tier: Manages session persistence, in-memory data tables, Excel clipboard ingestion, and CSV file serialization.
3. Mathematical Optimization Tier: Implements a Mixed Integer Linear Programming (MILP) model in Python using PuLP, interfacing with the open-source COIN-OR CBC branch-and-cut solver.
4. Analytics and Reporting Tier: Aggregates solver solutions into actionable fleet utilization metrics, turn-by-turn tanker mission logs, and downloadable operational schedules.

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

## Component Architecture and Data Flow

The following diagram outlines the runtime interaction and data transformations between user inputs, internal state caches, the mathematical solver, and visualization outputs:

```text
User Interaction (Browser)
│
├── File Upload (CSV) / In-Browser Table Edit / Excel Paste (Ctrl+V)
│
▼
Streamlit Session State (st.session_state)
│
├── tankers: DataFrame [Tanker, Capacity, Hire Rate]
├── demand: DataFrame [Unloading Port, Demand]
├── trip_LU: DataFrame [Loading Port x Unloading Ports]
└── trip_UU: DataFrame [Unloading Port 1 x Unloading Ports 2]
│
▼
Data Preparation Engine (prepare_optimization_input)
│
├── Dictionaries: tanker_capacity, tanker_hire_rate, demand
└── Nested Matrices: trip_time_LU[l][u], trip_time_UU[u1][u2]
│
▼
MILP Model Formulation (optimize function in app.py / HP.py)
│
├── Decision Variable Instantiation:
│   ├── Integer Variables: y[t, l, u1, None] and y[t, l, u1, u2]
│   └── Continuous Variables: x[t, l, u1, None, u1], x[t, l, u1, u2, u1], x[t, l, u1, u2, u2]
│
├── Objective Function Construction:
│   └── Minimize Total Fleet Charter Cost = sum(HireRate x VoyageDuration x Trips)
│
└── Constraint Formulation:
    ├── Demand Satisfaction: sum(Cargo Delivered to u) >= Demand[u]
    ├── Capacity Coupling: sum(Cargo on Route) <= Capacity[t] x Trips
    └── Operational Working Limit: sum(Voyage Duration x Trips) <= MaxDays
│
▼
COIN-OR CBC Solver Execution
│
▼
Solution Post-Processing and Output Generation
│
├── Infeasibility Detection and User Alerting
├── Metric Computation (Total Cost, Active Tankers, Route Count, Total Trips)
├── Fleet Utilization and Loading Port Charts
├── Tanker Mission Logs (Turn-by-turn operations)
└── Schedule DataFrame Generation and CSV Download
```

---

## Detailed Mathematical Architecture

The underlying mathematical model belongs to the class of Mixed Integer Linear Programming (MILP) formulations tailored for maritime routing and fleet scheduling.

### 1. Index Sets

- t in T = {T1, T2, T3, T4, T5, T6, T7, T8, T9}: Coastal tanker vessels.
- l in L = {L1, L2, L3, L4, L5, L6}: Refinery loading ports.
- u, u1, u2 in U = {U1, U2, ..., U11}: Destination unloading terminals.

### 2. Operational Parameters

- Capacity[t]: Physical cargo deadweight carrying capacity of tanker t in metric tonnes.
- HireRate[t]: Daily time-charter hire rate for tanker t in ₹ Crores per day.
- Demand[u]: Monthly liquid bulk demand at unloading port u in metric tonnes.
- TripTime_LU[l][u1]: Combined transit, berthing, loading, and discharging duration in days from loading port l to first discharge port u1.
- TripTime_UU[u1][u2]: Inter-port coastal transit and second berth discharge duration in days from unloading port u1 to unloading port u2.
- MaxDays: Maximum operational days allocated to each tanker per calendar month (default 30.0 days).

### 3. Decision Variable Formulation

The decision space separates discrete route execution from continuous cargo allocation:

- Voyage Decision Variables (Integer):
  - y[t, l, u1, None] in {0, 1, 2, ...}: Number of voyages executed by tanker t loading at l and discharging exclusively at u1.
  - y[t, l, u1, u2] in {0, 1, 2, ...} (where u1 != u2): Number of voyages executed by tanker t loading at l and performing a split discharge first at u1 and subsequently at u2.

- Cargo Allocation Decision Variables (Continuous):
  - x[t, l, u1, None, u1] >= 0: Total metric tonnes of cargo delivered to u1 across all single-port voyages by tanker t from loading port l.
  - x[t, l, u1, u2, u1] >= 0: Total metric tonnes of cargo discharged at first port u1 on two-port voyages by tanker t loading at l.
  - x[t, l, u1, u2, u2] >= 0: Total metric tonnes of cargo discharged at second port u2 on two-port voyages by tanker t loading at l.

### 4. Objective Function

The objective is to minimize total fleet charter hire transportation expenditure over the planning horizon:

Minimize:
Sum over all t in T, l in L, u1 in U:
HireRate[t] x TripTime_LU[l][u1] x y[t, l, u1, None]
+
Sum over all t in T, l in L, u1 in U, u2 in U (u1 != u2):
HireRate[t] x (TripTime_LU[l][u1] + TripTime_UU[u1][u2]) x y[t, l, u1, u2]

### 5. Constraint Formulations

#### Demand Fulfillment Constraint
Ensures that the aggregate volume of petroleum delivered to every coastal terminal u satisfies its monthly consumption requirement:

For every u in U:
Sum over all single-port trips delivering to u:
x[t, l, u, None, u]
+
Sum over all two-port trips where u is the first port:
x[t, l, u, u2, u]
+
Sum over all two-port trips where u is the second port:
x[t, l, u1, u, u]
>= Demand[u]

#### Vessel Payload Capacity Coupling Constraint
A fundamental requirement refined in Version 5 and Version 6 of the architecture: the sum of cargo discharged across all ports on any specific voyage itinerary cannot exceed the rated deadweight carrying capacity of the assigned vessel multiplied by the number of trips made on that itinerary.

For each single-port route (t, l, u1, None):
x[t, l, u1, None, u1] <= Capacity[t] x y[t, l, u1, None]

For each two-port split route (t, l, u1, u2):
x[t, l, u1, u2, u1] + x[t, l, u1, u2, u2] <= Capacity[t] x y[t, l, u1, u2]

This linear coupling guarantees that:
- Cargo can only be transported if integer trips y > 0 are scheduled.
- The model maintains complete freedom to split cargo between u1 and u2 (for example, delivering 30,000 MT to u1 and 20,000 MT to u2 on a 50,000 MT vessel) without exceeding vessel deadweight.

#### Vessel Monthly Working Days Constraint
Vessels cannot exceed their monthly availability window. The sum of transit and discharge durations across all assigned itineraries for tanker t must satisfy:

For every t in T:
Sum over all l in L, u1 in U of:
TripTime_LU[l][u1] x y[t, l, u1, None]
+
Sum over all l in L, u1 in U, u2 in U (u1 != u2) of:
(TripTime_LU[l][u1] + TripTime_UU[u1][u2]) x y[t, l, u1, u2]
<= MaxDays

The default value is 30.0 days, representing a full operational month.

---

## Data Schemas and Structure

### 1. Tanker Fleet Schema (DataFrame: tankers)
- Tanker (string): Unique vessel identifier (T1 through T9).
- Capacity (numeric): Deadweight carrying capacity in metric tonnes (e.g. 50,000 or 25,000).
- Hire Rate (numeric): Daily charter rate in ₹ Crores per day (e.g. 0.38 to 0.65).

### 2. Destination Port Demand Schema (DataFrame: demand)
- Unloading Port (string): Destination terminal identifier (U1 through U11).
- Demand (numeric): Monthly bulk requirement in metric tonnes (e.g. 5,000 to 135,000).

### 3. Loading to Unloading Transit Matrix Schema (DataFrame: trip_LU)
- Loading Port (string): Primary refinery terminal (L1 through L6).
- U1 to U11 (numeric): Transit and handling duration in days from loading port to each unloading terminal.

### 4. Inter-Terminal Transit Matrix Schema (DataFrame: trip_UU)
- Unloading Port 1 (string): First discharge terminal (U1 through U11).
- U1 to U11 (numeric): Inter-port transit and handling duration in days to second discharge terminal. Diagonal entries represent same-port transitions and are ignored by routing logic (u1 != u2).

### 5. Optimized Schedule Output Schema (DataFrame: df)
- Tanker (string): Assigned vessel identifier.
- Loading Port (string): Assigned loading refinery.
- Unload Port 1 (string): Primary discharge port.
- Unload Port 2 (string): Secondary discharge port (or hyphen '-' for single-port trips).
- Trips (integer): Number of completed voyages on this route.
- Cargo to U1 (numeric): Metric tonnes delivered to first unloading port.
- Cargo to U2 (numeric): Metric tonnes delivered to second unloading port (0 for single-port trips).

---

## Project Structure and File Organization

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

### Module Responsibilities

- app.py: Main entry point for the interactive web application. Contains Streamlit layout definitions, session state initialization, data editor configuration, optimization execution wrapper, and multi-tab visualization components.
- HP.py: Standalone programmatic optimization script containing example data definitions (example_hpcl_instance) and direct PuLP model execution for headless server environments or automated batch pipelines.
- Architecture.md: Complete technical and mathematical architecture specification.
- README.md: Primary project documentation, installation instructions, user guide, and industrial problem context.
- Backup/: Versioned archive documenting the iterative development and structural evolution of the software.

---

## Evolutionary Architecture (Version Progression)

The project underwent iterative enhancements documented in the Backup/ directory:

### Version 1 (Baseline Prototype)
- Initial command-line implementation of the single-loading and single-discharge model.
- Demonstrated feasibility of using PuLP and COIN-OR CBC for coastal tanker allocation.

### Version 2 (Initial Streamlit Integration)
- Ported command-line script to an interactive Streamlit application.
- Added basic sidebar parameters and tabular schedule presentation.

### Version 3 (Dynamic Data Management)
- Introduced editable Streamlit data tables allowing users to modify tanker capacities, demands, and hire rates directly in the browser.
- Implemented file uploader functionality for CSV data ingestion.

### Version 4 (Two-Port Split Discharge Formulation)
- Expanded mathematical model to incorporate dual-discharge itineraries (L -> U1 -> U2).
- Enabled split deliveries to capture logistical cost savings when serving geographically adjacent depots.

### Version 5 (Capacity Coupling Optimization)
- Identified and resolved a critical mathematical formulation issue where cargo allocation variables were not properly bounded by individual voyage capacities.
- Introduced rigorous coupling: sum of cargo deliveries across u1 and u2 strictly bounded by Capacity[t] x y[t, l, u1, u2].

### Version 6 (Enterprise Dashboard and Analytics)
- Re-architected user interface into dedicated analytical tabs:
  - Tab 1: Deployment Overview (utilization bar charts and turn-by-turn tanker mission logs).
  - Tab 2: Detailed Schedule (complete route table and CSV export).
  - Tab 3: Analytics and Route Insights (single-stop vs multi-stop ratio and top 5 frequent routes).
- Added real-time infeasibility detection with descriptive error feedback.
- Enabled Excel clipboard copy-paste (Ctrl+V) directly into data grids.

---

## Computational Complexity and Scalability

### Problem Dimension Analysis

For the baseline HPCL challenge instance:
- Tankers (|T|): 9
- Loading Ports (|L|): 6
- Unloading Ports (|U|): 11

### Variable Space

1. Single-port integer trip variables:
|T| x |L| x |U| = 9 x 6 x 11 = 594 variables

2. Two-port integer trip variables:
|T| x |L| x |U| x (|U| - 1) = 9 x 6 x 11 x 10 = 5,940 variables

Total integer decision variables (y) = 6,534 variables

3. Cargo allocation continuous variables:
- Single-port cargo (x): 594 variables
- Two-port cargo split (x for u1 and x for u2): 2 x 5,940 = 11,880 variables

Total continuous decision variables (x) = 12,474 variables

Total Decision Variables = 19,008 variables

### Constraint Count

- Demand satisfaction constraints: |U| = 11
- Capacity coupling constraints: 594 + 5,940 = 6,534
- Tanker monthly operating days constraints: |T| = 9

Total Structural Constraints = 6,554 constraints

### Solver Performance

Despite having over 19,000 variables, the problem exhibits a tight LP relaxation structure. When solved using the COIN-OR CBC branch-and-cut algorithm on standard commodity hardware:
- Presolve reduces trivial and unpromising route combinations.
- The optimal integer solution is typically discovered within 1.0 to 3.0 seconds.
- Memory consumption remains below 150 MB during model generation and solving.

---

## Authors and Acknowledgments

### Lead Developer
- Dhruv Mahendra Kajare

### Team Members
- Juhi Nale
- Neha Tarmale

### Acknowledgments
Developed as part of the HP Power Lab 2.0 Challenge organized by Hindustan Petroleum Corporation Limited (HPCL). This system demonstrates the application of Mixed Integer Linear Programming (MILP) and operations research to maritime petroleum supply chains, vessel chartering optimization, and coastal fleet routing.
