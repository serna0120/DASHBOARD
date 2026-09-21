import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State, dash_table, callback
import dash_bootstrap_components as dbc
from pathlib import Path

# Cargar datos
app_dir = Path(__file__).parent
tips = pd.read_csv(app_dir / "tips.csv")

bill_min = tips["total_bill"].min()
bill_max = tips["total_bill"].max()

# Inicializar App con un tema ligero y tipografia mas amable
app = Dash(__name__, external_stylesheets=[
    dbc.themes.FLATLY,
    dbc.icons.FONT_AWESOME,
    "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap",
])
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Analitica de propinas</title>
        {%favicon%}
        {%css%}
        <style>
            .kpi-icon {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.05rem;
            }
            .kpi-teal { background: #e1f5f2; color: #16a085; }
            .kpi-blue { background: #e5effa; color: #3276b1; }
            .kpi-orange { background: #fff0df; color: #e67e22; }
            .kpi-purple { background: #eee9fa; color: #7654a3; }
            .card-header {
                background: #fff;
                border-bottom: 1px solid #edf1f4;
                color: #183b56;
                font-weight: 700;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td,
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                font-family: 'DM Sans', sans-serif;
                font-size: 0.82rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# Layout (UI)
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div("ANALITICA DEL RESTAURANTE", className="text-uppercase small fw-bold", style={"color": "#16a085", "letterSpacing": "2px"}),
                html.H1("Panel de propinas", className="display-6 fw-bold mb-1", style={"color": "#183b56"}),
                html.P("Explora el comportamiento de las propinas y encuentra patrones en tu servicio.", className="text-muted mb-0"),
                html.Div("María Valentina Serna González", className="small mt-1", style={"color": "#718096", "fontSize": "0.78rem"}),
            ], md=8),
            dbc.Col(
                html.Div([
                    html.I(className="fas fa-chart-line me-2"),
                    "RESUMEN EN VIVO",
                ], className="text-end small fw-bold mt-3 mt-md-0", style={"color": "#16a085", "letterSpacing": "1px"}),
                md=4,
            ),
        ], className="align-items-center mb-4"),

        dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.Div([
                    html.I(className="fas fa-sliders-h me-2", style={"color": "#16a085"}),
                    html.Span("FILTROS", className="fw-bold small", style={"letterSpacing": "1px"}),
                ], className="mb-3"),
                html.Label("Importe de la cuenta", className="fw-semibold mb-2"),
                dcc.RangeSlider(
                    id="total_bill",
                    min=bill_min, max=bill_max,
                    value=[bill_min, bill_max],
                    marks={int(bill_min): f"${int(bill_min)}", int(bill_max): f"${int(bill_max)}"},
                    tooltip={"always_visible": False, "placement": "bottom"}
                ),
                html.Br(),
                html.Label("Servicio", className="fw-semibold mb-2"),
                dbc.Checklist(
                    id="time",
                    options=[{"label": "Almuerzo", "value": "Lunch"}, {"label": "Cena", "value": "Dinner"}],
                    value=["Lunch", "Dinner"],
                    inline=True
                ),
                html.Br(),
                dbc.Button([html.I(className="fas fa-rotate-left me-2"), "Restablecer filtros"], id="reset", color="dark", outline=True, className="w-100")
            ], className="p-4 bg-white border-0 rounded-3 shadow-sm")
        ], width=3),

        # Contenido Principal
        dbc.Col([
            # Fila de Value Boxes
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Div([html.I(className="fas fa-users")], className="kpi-icon kpi-teal"),
                        html.Div("TOTAL DE CLIENTES", className="small fw-bold text-muted mt-3"),
                        html.H2(id="total_tippers", className="fw-bold mb-0", style={"color": "#183b56"}),
                    ])
                ], className="border-0 shadow-sm h-100"), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Div([html.I(className="fas fa-receipt")], className="kpi-icon kpi-blue"),
                        html.Div("CUENTA PROMEDIO", className="small fw-bold text-muted mt-3"),
                        html.H2(id="average_bill", className="fw-bold mb-0", style={"color": "#183b56"}),
                    ])
                ], className="border-0 shadow-sm h-100"), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Div([html.I(className="fas fa-hand-holding-dollar")], className="kpi-icon kpi-orange"),
                        html.Div("PROPINA PROMEDIO", className="small fw-bold text-muted mt-3"),
                        html.H2(id="average_tip", className="fw-bold mb-0", style={"color": "#183b56"}),
                    ])
                ], className="border-0 shadow-sm h-100"), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Div([html.I(className="fas fa-sack-dollar")], className="kpi-icon kpi-purple"),
                        html.Div("VENTAS TOTALES", className="small fw-bold text-muted mt-3"),
                        html.H2(id="total_revenue", className="fw-bold mb-0", style={"color": "#183b56"}),
                    ])
                ], className="border-0 shadow-sm h-100"), width=3),
            ], className="mb-3"),

            # Fila de Tabla y Gráfico
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Datos de propinas"),
                    dbc.CardBody(html.Div(id="table_container"), style={"maxHeight": "430px", "overflowY": "auto"})
                ], className="border-0 shadow-sm h-100"), width=5),
                dbc.Col(dbc.Card([
                    dbc.CardHeader([
                        "Cuenta total vs propina",
                        dbc.Button(html.I(className="fas fa-ellipsis-v"), id="open_popover", color="link", size="sm", className="float-end"),
                        dbc.Popover([
                            dbc.PopoverHeader("Añadir variable de color"),
                            dbc.PopoverBody(
                                dbc.RadioItems(
                                    id="scatter_color",
                                    options=[
                                        {"label": "Sin color", "value": "none"},
                                        {"label": "Sexo", "value": "sex"},
                                        {"label": "Fumador", "value": "smoker"},
                                        {"label": "Día", "value": "day"},
                                        {"label": "Servicio", "value": "time"},
                                    ],
                                    value="none",
                                    inline=True
                                )
                            )
                        ], target="open_popover", trigger="click", placement="top")
                    ]),
                    dbc.CardBody(dcc.Graph(id="scatterplot", config={"displayModeBar": False}))
                ], className="border-0 shadow-sm h-100"), width=7),
            ])
            , dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Propina media por día"),
                    dbc.CardBody(dcc.Graph(id="tip_by_day", config={"displayModeBar": False}))
                ], className="border-0 shadow-sm h-100"), width=5),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Distribución por servicio"),
                    dbc.CardBody(dcc.Graph(id="service_mix", config={"displayModeBar": False}))
                ], className="border-0 shadow-sm h-100"), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Distribución de cuentas"),
                    dbc.CardBody(dcc.Graph(id="bill_distribution", config={"displayModeBar": False}))
                ], className="border-0 shadow-sm h-100"), width=3),
            ], className="mt-4")
        ], width=9)
        ], className="g-4"),
    ], fluid=True, className="py-4"),
], style={"background": "linear-gradient(135deg, #e3f3f0 0%, #f8f3e8 54%, #e8eff7 100%)", "minHeight": "100vh", "fontFamily": "'DM Sans', sans-serif"})

# Callbacks (Lógica)

@callback(
    Output("total_tippers", "children"),
    Output("average_bill", "children"),
    Output("average_tip", "children"),
    Output("total_revenue", "children"),
    Output("table_container", "children"),
    Output("scatterplot", "figure"),
    Output("tip_by_day", "figure"),
    Output("service_mix", "figure"),
    Output("bill_distribution", "figure"),
    Input("total_bill", "value"),
    Input("time", "value"),
    Input("scatter_color", "value")
)
def update_dashboard(bill_rng, time_val, color_val):
    # Filtrado (Equivalente a tips_data() reactivo)
    df = tips[
        (tips["total_bill"].between(bill_rng[0], bill_rng[1])) & 
        (tips["time"].isin(time_val))
    ]
    
    # Cálculos
    tippers = len(df)
    avg_bill = f"${df['total_bill'].mean():.2f}" if not df.empty else "N/A"
    avg_tip = f"${df['tip'].mean():.2f}" if not df.empty else "N/A"
    total_revenue = f"${df['total_bill'].sum():,.0f}" if not df.empty else "N/A"
    
    # Tabla
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": {
            "total_bill": "Cuenta total",
            "tip": "Propina",
            "sex": "Sexo",
            "smoker": "Fumador",
            "day": "Día",
            "time": "Servicio",
            "size": "Personas",
        }.get(i, i), "id": i} for i in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#183b56', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left', 'padding': '9px', 'border': '1px solid #edf1f4'},
    )
    
    # Gráfico
    color_arg = None if color_val == "none" else color_val
    fig = px.scatter(df, x="total_bill", y="tip", color=color_arg, trendline="lowess" if not df.empty else None)
    fig.update_traces(marker={"size": 9, "opacity": 0.75})
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans, sans-serif", "color": "#52606d"},
        xaxis_title="Total bill ($)",
        yaxis_title="Tip ($)",
        legend_title_text="",
    )

    day_labels = {"Thur": "Jueves", "Fri": "Viernes", "Sat": "Sábado", "Sun": "Domingo"}
    day_summary = df.groupby("day", as_index=False).agg(avg_tip=("tip", "mean"))
    day_summary["day_label"] = day_summary["day"].map(day_labels)
    day_summary["day_label"] = pd.Categorical(
        day_summary["day_label"], categories=["Jueves", "Viernes", "Sábado", "Domingo"], ordered=True
    )
    tip_by_day = px.bar(
        day_summary.sort_values("day_label"), x="day_label", y="avg_tip",
        color="avg_tip", color_continuous_scale=["#d8f2ed", "#16a085"],
        labels={"day_label": "Día", "avg_tip": "Propina media"},
    )

    service_summary = df["time"].map({"Lunch": "Almuerzo", "Dinner": "Cena"}).value_counts().reset_index()
    service_summary.columns = ["service", "visits"]
    service_mix = px.pie(
        service_summary, names="service", values="visits", hole=0.58,
        color_discrete_sequence=["#16a085", "#f2a65a"],
        labels={"service": "Servicio", "visits": "Visitas"},
    )
    service_mix.update_traces(textposition="inside", textinfo="percent+label")

    bill_distribution = px.histogram(
        df, x="total_bill", nbins=12, color_discrete_sequence=["#3276b1"],
        labels={"total_bill": "Cuenta total", "count": "Visitas"},
    )
    for chart in [tip_by_day, service_mix, bill_distribution]:
        chart.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "DM Sans, sans-serif", "color": "#52606d"},
        )
    tip_by_day.update_layout(coloraxis_showscale=False)
    bill_distribution.update_layout(bargap=0.12)

    return tippers, avg_bill, avg_tip, total_revenue, table, fig, tip_by_day, service_mix, bill_distribution

# Callback para Reset
@callback(
    Output("total_bill", "value"),
    Output("time", "value"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n):
    return [bill_min, bill_max], ["Lunch", "Dinner"]

if __name__ == "__main__":
    app.run()