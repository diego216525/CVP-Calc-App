# CVP Analysis Platform

A multi-product cost-volume-profit analytics dashboard built with Streamlit and Plotly.

## Features

- **Break-even Analysis** — visual chart with profit/loss zone shading, fixed cost line, and break-even marker
- **Target Profit Calculator** — enter a desired profit to see the units and revenue required
- **Key Metrics** — net operating income, break-even (units and dollars), CM ratio, margin of safety, operating leverage
- **Product Breakdown** — per-product contribution margin, CM ratio, and revenue mix visualization
- **Scenario Manager** — save, compare, and clear what-if scenarios with side-by-side bar charts
- **Multi-Variable Sensitivity** — toggle between price, variable cost, and volume to see profit impact
- **Profit Heatmap** — price vs. variable cost grid showing profit across combinations
- **CSV Support** — upload product data via CSV or enter manually; export results as CSV

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run CVPAPP.py
```

The app will open in your browser. Enter product data manually using the input fields, or upload a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `SP` | Selling price per unit |
| `VC` | Variable cost per unit |
| `Q` | Quantity sold |
_Add screenshots of your dashboard here._

## License

MIT
