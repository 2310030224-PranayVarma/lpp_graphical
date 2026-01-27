import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import random

st.set_page_config(page_title="LPP Graphical Solver", layout="wide")
st.title("Linear Programming Problem – Graphical Method")

st.markdown("---")

# ================= INPUT =================
col1, col2 = st.columns(2)

with col1:
    opt_type = st.selectbox("Optimization Type", ["Maximization", "Minimization"])
    n = st.number_input("Number of Constraints", 1, 6, 2)

with col2:
    st.markdown("### Objective Function")
    z1 = st.number_input("Coefficient of x₁", value=4.0)
    z2 = st.number_input("Coefficient of x₂", value=6.0)

st.markdown("### Constraints (a·x₁ + b·x₂ ≤ / ≥ c)")

constraints = []
for i in range(n):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        a = st.number_input(f"a{i+1}", value=1.0, key=f"a{i}")
    with c2:
        b = st.number_input(f"b{i+1}", value=1.0, key=f"b{i}")
    with c3:
        op = st.selectbox(f"Op{i+1}", ["<=", ">="], key=f"op{i}")
    with c4:
        c = st.number_input(f"c{i+1}", value=0.0, key=f"c{i}")
    constraints.append((a, b, c, op))

st.markdown("---")

# ================= SOLVE =================
if st.button("Solve LPP"):

    # ---------- GRID (FIRST QUADRANT) ----------
    x = np.linspace(0, 15, 600)
    y = np.linspace(0, 15, 600)
    X, Y = np.meshgrid(x, y)

    feasible = (X >= 0) & (Y >= 0)

    for a, b, c, op in constraints:
        expr = a * X + b * Y
        if op == "<=":
            feasible &= (expr <= c + 1e-6)
        else:
            feasible &= (expr >= c - 1e-6)

    fig = go.Figure()

    # ---------- FEASIBLE REGION ----------
    r, g, b = [random.randint(100, 200) for _ in range(3)]
    region_color = f"rgba({r},{g},{b},0.35)"

    fig.add_trace(
        go.Contour(
            x=x,
            y=y,
            z=feasible.astype(int),
            showscale=False,
            contours=dict(coloring="fill"),
            colorscale=[[0, "rgba(0,0,0,0)"], [1, region_color]],
            hoverinfo="skip",
            name="Feasible Region"
        )
    )

    # ---------- CONSTRAINT LINES ----------
    palette = px.colors.qualitative.Set1

    for idx, (a, b, c, _) in enumerate(constraints):
        color = palette[idx % len(palette)]
        if abs(b) > 1e-6:
            y_line = (c - a * x) / b
            fig.add_trace(go.Scatter(
                x=x,
                y=y_line,
                mode="lines",
                line=dict(color=color, width=3),
                name=f"C{idx+1}: {a}x₁ + {b}x₂ = {c}"
            ))
        else:
            fig.add_vline(
                x=c / a,
                line=dict(color=color, width=3),
                annotation_text=f"C{idx+1}"
            )

    # ---------- FIND CORNER POINTS (COMPLETE) ----------
    points = []

    # intersections of constraint lines
    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            a1, b1, c1, _ = constraints[i]
            a2, b2, c2, _ = constraints[j]
            A = np.array([[a1, b1], [a2, b2]])
            B = np.array([c1, c2])
            if abs(np.linalg.det(A)) > 1e-6:
                points.append(np.linalg.solve(A, B))

    # intersections with x₁ = 0
    for a, b, c, _ in constraints:
        if abs(b) > 1e-6:
            points.append([0, c / b])

    # intersections with x₂ = 0
    for a, b, c, _ in constraints:
        if abs(a) > 1e-6:
            points.append([c / a, 0])

    # origin
    points.append([0, 0])

    feasible_pts = []
    for x1, x2 in points:
        if x1 < -1e-6 or x2 < -1e-6:
            continue
        ok = True
        for a, b, c, op in constraints:
            val = a * x1 + b * x2
            if op == "<=" and val > c + 1e-6:
                ok = False
            if op == ">=" and val < c - 1e-6:
                ok = False
        if ok:
            feasible_pts.append((round(x1, 4), round(x2, 4)))

    feasible_pts = list(set(feasible_pts))

    # ---------- OBJECTIVE ----------
    if feasible_pts:
        results = [(x1, x2, z1 * x1 + z2 * x2) for x1, x2 in feasible_pts]
        best = min(results, key=lambda x: x[2]) if opt_type == "Minimization" else max(results, key=lambda x: x[2])

        # Corner points
        fig.add_trace(go.Scatter(
            x=[p[0] for p in feasible_pts],
            y=[p[1] for p in feasible_pts],
            mode="markers",
            marker=dict(color="red", size=10),
            name="Corner Points"
        ))

        # Optimal point
        fig.add_trace(go.Scatter(
            x=[best[0]],
            y=[best[1]],
            mode="markers",
            marker=dict(color="green", size=15),
            name="Optimal Point"
        ))

        st.success(f"Optimal Solution: x₁ = {best[0]:.3f}, x₂ = {best[1]:.3f}")
        st.success(f"Optimal Z Value = {best[2]:.3f}")

    # ---------- LAYOUT ----------
    fig.update_layout(
        xaxis=dict(title="x₁", range=[0, 10], zeroline=True),
        yaxis=dict(title="x₂", range=[0, 10], zeroline=True),
        dragmode="pan",
        template="plotly_white",
        height=600,
        legend=dict(x=1.02, y=1)
    )

    st.plotly_chart(fig, use_container_width=True)
