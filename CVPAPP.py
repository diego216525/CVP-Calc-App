import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="CVP Analysis Platform", layout="wide")

st.markdown("""
<style>
.main {background-color: #0e1117;}
.block-container {padding-top: 2rem;}
.stMetric {
    background: #161b22;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #30363d;
}
h1 {font-size: 2.2rem;}
h2 {margin-top: 1rem;}
</style>
""", unsafe_allow_html=True)

if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}

st.sidebar.title("Controls")

fixed_cost = st.sidebar.number_input("Fixed Cost ($)", value=5000.0, min_value=0.0)

st.sidebar.markdown("### Scenario Adjustments")
price_adj = st.sidebar.slider("Price Adjustment (%)", -50, 50, 0)
cost_adj = st.sidebar.slider("Cost Adjustment (%)", -50, 50, 0)
demand_adj = st.sidebar.slider("Demand Adjustment (%)", -50, 50, 0)

st.sidebar.markdown("### Data Input")
upload = st.sidebar.file_uploader("Upload CSV", type=["csv"])
num_products = st.sidebar.number_input("Number of Products", 1, 20, 3)

st.title("CVP Analysis Platform")
st.caption("Multi-product cost-volume-profit analytics")

products = []
df = None

if upload:
    try:
        df = pd.read_csv(upload)
        required_cols = {"SP", "VC", "Q"}
        if not required_cols.issubset(df.columns):
            st.error(
                f"CSV must contain columns: {', '.join(sorted(required_cols))}. "
                f"Found: {', '.join(df.columns.tolist())}"
            )
            df = None
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        df = None

if df is None and not upload:
    for i in range(1, int(num_products) + 1):
        cols = st.columns(3)
        with cols[0]:
            sp = st.number_input(f"Price {i}", value=10.0, min_value=0.01, key=f"sp{i}")
        with cols[1]:
            vc = st.number_input(f"Variable Cost {i}", value=5.0, min_value=0.0, key=f"vc{i}")
        with cols[2]:
            q = st.number_input(f"Quantity {i}", value=500.0, min_value=0.0, key=f"q{i}")

        products.append({"Product": f"P{i}", "SP": sp, "VC": vc, "Q": q})

    df = pd.DataFrame(products)

if df is not None and not df.empty:
    df["SP"] = df["SP"] * (1 + price_adj / 100)
    df["VC"] = df["VC"] * (1 + cost_adj / 100)
    df["Q"] = df["Q"] * (1 + demand_adj / 100)
    df = df[df["Q"] > 0].copy()

if df is not None and not df.empty:

    df["Revenue"] = df["SP"] * df["Q"]
    df["VC_total"] = df["VC"] * df["Q"]
    df["CM"] = df["Revenue"] - df["VC_total"]
    df["CM_per_unit"] = df["SP"] - df["VC"]
    df["CM_ratio_pct"] = (df["CM_per_unit"] / df["SP"] * 100).round(1)

    total_rev = df["Revenue"].sum()
    total_vc = df["VC_total"].sum()
    total_cm = df["CM"].sum()
    total_q = df["Q"].sum()

    cm_per_unit = total_cm / total_q if total_q > 0 else 0
    cm_ratio = total_cm / total_rev if total_rev > 0 else 0
    break_even_units = fixed_cost / cm_per_unit if cm_per_unit > 0 else float("inf")
    break_even_dollars = break_even_units * (total_rev / total_q) if total_q > 0 and break_even_units != float("inf") else float("inf")
    noi = total_cm - fixed_cost
    margin_of_safety = ((total_q - break_even_units) / total_q * 100) if total_q > 0 and break_even_units != float("inf") else 0
    operating_leverage = total_cm / noi if noi != 0 else float("inf")

    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Scenarios", "Sensitivity", "Heatmap"])

    with tab1:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Net Operating Income", f"${noi:,.0f}")
        c2.metric("Break-even (units)", f"{break_even_units:,.0f}")
        c3.metric("Break-even ($)", f"${break_even_dollars:,.0f}" if break_even_dollars != float("inf") else "N/A")
        c4.metric("CM Ratio", f"{cm_ratio:.2%}")
        c5.metric("Margin of Safety", f"{margin_of_safety:.1f}%")
        c6.metric("Operating Leverage", f"{operating_leverage:.2f}x" if operating_leverage != float("inf") else "N/A")

        st.markdown("### Target Profit Calculator")
        target_cols = st.columns([2, 2, 2])
        with target_cols[0]:
            target_profit = st.number_input("Target Profit ($)", value=10000.0, min_value=0.0, step=1000.0)
        target_units = (fixed_cost + target_profit) / cm_per_unit if cm_per_unit > 0 else float("inf")
        target_revenue = target_units * (total_rev / total_q) if total_q > 0 and target_units != float("inf") else float("inf")
        with target_cols[1]:
            st.metric("Units Required", f"{target_units:,.0f}" if target_units != float("inf") else "N/A")
        with target_cols[2]:
            st.metric("Revenue Required", f"${target_revenue:,.0f}" if target_revenue != float("inf") else "N/A")

        st.markdown("### Product Breakdown")

        display_df = df.rename(columns={
            "SP": "Selling Price",
            "VC": "Variable Cost",
            "Q": "Quantity",
            "VC_total": "Total Variable Cost",
            "CM": "Contribution Margin",
            "CM_per_unit": "CM / Unit",
            "CM_ratio_pct": "CM Ratio (%)",
        }).round(2)

        st.dataframe(display_df, use_container_width=True)

        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name="cvp_product_breakdown.csv",
            mime="text/csv",
        )

        st.markdown("### Break-even Analysis")
        units = np.linspace(0, total_q * 1.5, 200)
        rev_per_unit = total_rev / total_q if total_q > 0 else 0
        vc_per_unit = total_vc / total_q if total_q > 0 else 0

        revenue_line = rev_per_unit * units
        cost_line = fixed_cost + vc_per_unit * units

        fig = go.Figure()

        if break_even_units != float("inf"):
            profit_units = units[units >= break_even_units]
            if len(profit_units) > 0:
                fig.add_trace(go.Scatter(
                    x=profit_units, y=rev_per_unit * profit_units,
                    line=dict(width=0), showlegend=False, hoverinfo="skip",
                ))
                fig.add_trace(go.Scatter(
                    x=profit_units, y=fixed_cost + vc_per_unit * profit_units,
                    fill="tonexty", fillcolor="rgba(46,204,113,0.1)",
                    line=dict(width=0), name="Profit Zone", hoverinfo="skip",
                ))

            loss_units = units[units <= break_even_units]
            if len(loss_units) > 0:
                fig.add_trace(go.Scatter(
                    x=loss_units, y=fixed_cost + vc_per_unit * loss_units,
                    line=dict(width=0), showlegend=False, hoverinfo="skip",
                ))
                fig.add_trace(go.Scatter(
                    x=loss_units, y=rev_per_unit * loss_units,
                    fill="tonexty", fillcolor="rgba(231,76,60,0.1)",
                    line=dict(width=0), name="Loss Zone", hoverinfo="skip",
                ))

        fig.add_trace(go.Scatter(
            x=units, y=revenue_line,
            name="Revenue", line=dict(width=3, color="#2ecc71"),
        ))
        fig.add_trace(go.Scatter(
            x=units, y=cost_line,
            name="Total Cost", line=dict(width=3, color="#e74c3c"),
        ))
        fig.add_trace(go.Scatter(
            x=units, y=[fixed_cost] * len(units),
            name="Fixed Cost", line=dict(width=2, color="#3498db", dash="dash"),
        ))
        if break_even_units != float("inf"):
            fig.add_trace(go.Scatter(
                x=[break_even_units],
                y=[fixed_cost + vc_per_unit * break_even_units],
                mode="markers",
                marker=dict(size=12, color="#f1c40f", line=dict(width=2, color="#fff")),
                name="Break-even Point",
            ))

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Units Sold",
            yaxis_title="Dollars ($)",
            height=500,
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        chart_left, chart_right = st.columns(2)

        with chart_left:
            cm_fig = go.Figure(go.Bar(
                x=df["Product"],
                y=df["CM"],
                marker_color="#3498db",
                text=df["CM"].round(0).astype(int).astype(str).apply(lambda x: f"${x}"),
                textposition="outside",
            ))
            cm_fig.update_layout(
                template="plotly_dark",
                title="Contribution Margin by Product",
                xaxis_title="Product",
                yaxis_title="Contribution Margin ($)",
                height=400,
            )
            st.plotly_chart(cm_fig, use_container_width=True)

        with chart_right:
            mix = go.Figure(data=[go.Pie(
                labels=df["Product"],
                values=df["Revenue"],
                hole=0.5,
            )])
            mix.update_layout(
                template="plotly_dark",
                title="Revenue Mix by Product",
                height=400,
            )
            st.plotly_chart(mix, use_container_width=True)

    with tab2:
        name = st.text_input("Scenario Name")

        if st.button("Save Scenario"):
            if name.strip():
                st.session_state.scenarios[name] = {
                    "Profit": round(noi, 2),
                    "Break-even (units)": round(break_even_units, 2),
                    "CM Ratio": f"{cm_ratio:.2%}",
                    "Revenue": round(total_rev, 2),
                    "Margin of Safety": f"{margin_of_safety:.1f}%",
                }
                st.success(f"Scenario '{name}' saved.")
            else:
                st.warning("Please enter a scenario name before saving.")

        if st.session_state.scenarios:
            st.markdown("### Saved Scenarios")
            scenario_df = pd.DataFrame(st.session_state.scenarios).T
            st.dataframe(scenario_df, use_container_width=True)

            if len(st.session_state.scenarios) >= 2:
                st.markdown("### Scenario Comparison")
                profit_vals = {k: v["Profit"] for k, v in st.session_state.scenarios.items()}
                comp_colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in profit_vals.values()]

                comp_fig = go.Figure(go.Bar(
                    x=list(profit_vals.keys()),
                    y=list(profit_vals.values()),
                    marker_color=comp_colors,
                    text=[f"${v:,.0f}" for v in profit_vals.values()],
                    textposition="outside",
                ))
                comp_fig.add_hline(y=0, line_dash="dash", line_color="#888")
                comp_fig.update_layout(
                    template="plotly_dark",
                    xaxis_title="Scenario",
                    yaxis_title="Net Operating Income ($)",
                    height=400,
                )
                st.plotly_chart(comp_fig, use_container_width=True)

            if st.button("Clear All Scenarios"):
                st.session_state.scenarios = {}
                st.rerun()

    with tab3:
        st.markdown("### Multi-Variable Sensitivity")
        sens_var = st.radio(
            "Variable to analyze",
            ["Price", "Variable Cost", "Volume"],
            horizontal=True,
        )

        changes = np.arange(-25, 26, 5)

        if sens_var == "Price":
            impacts = [(total_rev * (1 + c / 100) - total_vc - fixed_cost) for c in changes]
        elif sens_var == "Variable Cost":
            impacts = [(total_rev - total_vc * (1 + c / 100) - fixed_cost) for c in changes]
        else:
            impacts = [((total_rev - total_vc) * (1 + c / 100) - fixed_cost) for c in changes]

        colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in impacts]

        fig = go.Figure(go.Bar(
            x=changes,
            y=impacts,
            marker_color=colors,
            text=[f"${v:,.0f}" for v in impacts],
            textposition="outside",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#888", annotation_text="Break-even")
        fig.update_layout(
            template="plotly_dark",
            title=f"{sens_var} Sensitivity Impact on Profit",
            xaxis_title=f"{sens_var} Change (%)",
            yaxis_title="Net Operating Income ($)",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        avg_sp = df["SP"].mean()
        avg_vc = df["VC"].mean()
        price_range = np.linspace(avg_sp * 0.5, avg_sp * 1.5, 25)
        cost_range = np.linspace(avg_vc * 0.5, avg_vc * 1.5, 25)

        z = [[(p - c) * total_q - fixed_cost for p in price_range] for c in cost_range]

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=np.round(price_range, 2),
            y=np.round(cost_range, 2),
            colorscale="RdYlGn",
            colorbar=dict(title="Profit ($)"),
        ))
        fig.update_layout(
            template="plotly_dark",
            title="Profit Heatmap: Price vs. Variable Cost",
            xaxis_title="Selling Price ($)",
            yaxis_title="Variable Cost ($)",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Enter valid product data to begin analysis.")