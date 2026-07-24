# Coastal Vessel Optimization

### Maritime Logistics Optimization using Integer Linear Programming & Streamlit

A decision-support system developed for the **HP Power Lab 2.0 Challenge** that optimizes coastal tanker allocation for bulk cargo transportation. The system minimizes transportation costs by determining optimal tanker assignments, voyage plans, and cargo distribution while satisfying operational constraints.

The solution combines **Integer Linear Programming (PuLP)** with an interactive **Streamlit dashboard**, enabling users to modify tanker fleets, cargo demands, and trip durations before generating optimized transportation schedules.

---

## Overview

Efficient coastal shipping is critical for minimizing operational costs in bulk cargo transportation.

This project models the tanker allocation problem as an **Integer Linear Programming (ILP)** optimization problem where:

- Multiple coastal tankers transport cargo
- Each tanker loads from a single loading port
- Each voyage serves up to two unloading ports
- Demand at every destination must be fulfilled
- Transportation cost is minimized

The optimization engine automatically computes the best transportation plan while respecting tanker capacities, voyage durations, and monthly operational limits.

---

## Features

- Integer Linear Programming-based optimization
- Interactive Streamlit dashboard
- Tanker allocation optimization
- Cargo demand fulfillment
- Single-port loading constraint
- Two-port discharge optimization
- Transportation cost minimization
- Monthly working-day constraints
- Editable tanker, demand, and trip datasets
- Optimal voyage schedule generation

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

## Optimization Model

The optimization engine creates integer decision variables representing the number of trips performed by each tanker.

For every possible combination of:

- Tanker
- Loading Port
- First Discharge Port
- Optional Second Discharge Port

the model determines whether the trip should be included in the optimal transportation plan.

---

## Objective Function

The objective is to minimize the total transportation cost.

For every voyage:

```text
Trip Cost = Hire Rate × Voyage Time
```

The optimization minimizes the total cost across the entire fleet.

---

## Constraints

### Single Loading Port

Each voyage loads cargo from only one loading port.

### Maximum Two Discharge Ports

Each trip may unload cargo at:

- One unloading port
- Two unloading ports

### Demand Satisfaction

Demand for every unloading port must be fully satisfied.

### Monthly Working Limit

Each tanker operates within a configurable maximum number of working days.

### Capacity Constraint

Cargo transported on each trip cannot exceed the assigned tanker's carrying capacity.

---

## Streamlit Dashboard

The project includes an interactive web interface that allows users to:

- Edit tanker capacities
- Modify charter hire rates
- Update unloading port demands
- Change trip-time matrices
- Configure maximum working days
- Execute optimization
- View optimized transportation schedules

---

## Technologies Used

| Category | Technology |
|----------|------------|
| Language | Python |
| Optimization | PuLP |
| Solver | CBC Solver |
| Web Framework | Streamlit |
| Data Processing | Pandas |
| Numerical Computing | NumPy |

---

## Project Structure

```text
HPCL-Coastal-Vessel-Optimization/
│
├── app.py
├── HP.py
├── Backup/
│   ├── version1/
│   ├── version2/
│   ├── version3/
│   ├── version4/
│   ├── version5/
│   └── version6/
└── README.md
```

---

## Installation

```bash
git clone https://github.com/kajaredhruv433/kajaredhruv433-Coastal-Vessel-Optimization-HP-Power-Lab-2.0-.git

cd kajaredhruv433-Coastal-Vessel-Optimization-HP-Power-Lab-2.0-

pip install -r requirements.txt
```

---

## Requirements

```text
streamlit
pandas
numpy
pulp
```

---

## Running the Application

```bash
streamlit run app.py
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

## Output

The optimization engine generates:

- Tanker assignment
- Loading port
- Discharge port(s)
- Number of trips
- Cargo allocation
- Voyage duration
- Transportation cost
- Fleet utilization

---

## Applications

- Coastal Shipping Optimization
- Fleet Scheduling
- Bulk Cargo Logistics
- Supply Chain Planning
- Transportation Cost Optimization
- Operations Research
- Decision Support Systems

---

## Future Improvements

- Multi-objective optimization
- Fuel consumption optimization
- Carbon emission analysis
- Weather-aware voyage planning
- Real-time AIS integration
- Port congestion prediction
- Interactive route visualization
- Export to Excel and PDF

---

## Key Learnings

- Integer Linear Programming
- Operations Research
- Transportation Optimization
- Maritime Logistics
- Fleet Scheduling
- Constraint Modeling
- PuLP Optimization
- Streamlit Dashboard Development
- Data-Driven Decision Support

---

## Acknowledgements

Developed as part of **HP Power Lab 2.0**, this project demonstrates the application of Integer Linear Programming and optimization techniques to solve real-world maritime logistics challenges involving coastal tanker scheduling and transportation cost minimization.

---

⭐ **If you found this project useful, consider giving it a star!**
