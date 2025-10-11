# app_dash.py
import requests
import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import deque
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qrng-dashboard")

BACKEND_URL = "http://127.0.0.1:5000"
REFRESH_INTERVAL = 5000  # ms

COLORS = {
    "quantum_primary_light": "#00D474",
    "quantum_primary_dark":  "#4DFFB5",
    "quantum_secondary": "#00A896",
    "success": "#06D6A0",
    "warning": "#F4A261",
    "danger":  "#E63946",
    "info":    "#457B9D",
    "dark":    "#1D3557",
    "light":   "#F1FAEE",
    "quantum_glow": "#88FF88",
}

GRAPH_CONFIG = {"displaylogo": False, "displayModeBar": False}
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "QRNG Defense System - Quantum Foundation"

entropy_history = deque(maxlen=200)
qber_history = deque(maxlen=200)

def theme_settings(theme: str):
    if (theme or "light") == "dark":
        return "plotly_dark", COLORS["quantum_primary_dark"]
    return "plotly_white", COLORS["quantum_primary_light"]

def make_api_call(endpoint, method="GET", **kwargs):
    try:
        url = f"{BACKEND_URL}{endpoint}"
        r = requests.post(url, timeout=10, **kwargs) if method == "POST" else requests.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {endpoint} - {str(e)}")
        return {"error": str(e)}

def set_transparent(fig, template):
    fig.update_layout(template=template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def create_qrng_demo_figure(template, accent):
    sample_bits = "10110010110011101001010110011010"
    x = list(range(len(sample_bits))); y = [int(b) for b in sample_bits]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers+lines", name="Quantum Random Bits",
                             marker=dict(size=12, color=accent, line=dict(width=2, color="white")),
                             line=dict(width=2, color=accent)))
    fig.update_layout(title="QRNG Foundation: True Quantum Random Numbers",
                      xaxis_title="Bit Position", yaxis_title="Bit Value (0 or 1)",
                      height=300, showlegend=True, yaxis=dict(tickvals=[0, 1], range=[-0.1, 1.1]))
    return set_transparent(fig, template)

def create_entropy_gauge(entropy_value=0.95):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=entropy_value, domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Quantum Entropy Level"},
        delta={"reference": 1.0, "increasing": {"color": COLORS["success"]}},
        gauge={"axis": {"range": [None, 1.0]},
               "bar": {"color": COLORS["quantum_primary_light"]},
               "steps": [{"range": [0, 0.7], "color": COLORS["danger"]},
                         {"range": [0.7, 0.9], "color": COLORS["warning"]},
                         {"range": [0.9, 1.0], "color": COLORS["success"]}],
               "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 0.9}}
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def create_performance_comparison(template, accent):
    methods = ["QRNG (Quantum)", "Classical PRNG", "Hardware TRNG"]
    fig = go.Figure(data=[
        go.Bar(name="Energy Efficiency %", x=methods, y=[95, 60, 40], marker_color=accent),
        go.Bar(name="Security Level %", x=methods, y=[100, 70, 85], marker_color=COLORS["success"]),
    ])
    fig.update_layout(title="QRNG Performance Advantages", barmode="group",
                      height=300, yaxis_title="Performance Rating (%)")
    return set_transparent(fig, template)

# ---------------- Layout ----------------
app.layout = html.Div(id="page-root", className="theme-light", children=[
    dcc.Store(id="crypto-store"),
    dcc.Store(id="theme-store", data="light"),
    dcc.Interval(id="interval-component", interval=REFRESH_INTERVAL, n_intervals=0),

    dbc.Row([dbc.Col([
        html.Div([
            html.H1("🔬 Quantum Random Number Generator", className="text-center mb-2", id="title-color"),
            html.H4("Defense Security Foundation", className="text-center mb-2"),
            html.P("AQVH1910 - All defense capabilities powered by true quantum randomness",
                   className="text-center text-muted mb-3"),
            html.P("Design a basic QRNG using a quantum circuit that utilizes superposition (H) and measurement (M) to generate random bits.",
                   className="text-center fw-bold"),
            dbc.Button("🌓 Toggle Theme", id="toggle-theme", color="secondary", size="sm", className="ms-2"),
        ])
    ])]),
    dbc.Alert(id="qrng-status-alert",
              children="QRNG Foundation: Operational - Quantum Security Active",
              color="success", is_open=True, className="mb-3"),

    # QRNG core
    dbc.Card([
        dbc.CardHeader([html.H4("🎲 QRNG Foundation: True Quantum Random Numbers", className="mb-0",
                                 style={"color": "white"})], id="qrng-header"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P("True quantum randomness is the foundation of all defense security capabilities:", className="mb-2"),
                    html.Ul([
                        html.Li("🔐 Quantum key distribution (E91/BB84)"),
                        html.Li("🛡️ AI-powered security monitoring"),
                        html.Li("⚡ Energy-aware operations"),
                        html.Li("🌍 Environmental sustainability"),
                    ]),
                    dbc.Button("Generate Quantum Random Bits", id="generate-qrng-btn",
                               color="success", className="mt-2"),
                ], width=6),
                dbc.Col([dcc.Graph(id="qrng-demo-graph", config=GRAPH_CONFIG)], width=6),
            ]),
            dbc.Row([dbc.Col([html.Div(id="qrng-output", className="mt-3")], width=12)])
        ])
    ], className="mb-4"),

    # Control panel and health/datasets
    dbc.Card([
        dbc.CardHeader([html.H5("🎛️ QRNG Control & Health", className="mb-0")]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([dbc.Label("Quantum Shots per Generation:"),
                         dbc.Input(id="shots-input", type="number", value=1024, min=100, step=100)], width=3),
                dbc.Col([dbc.Label("Random Bits to Generate:"),
                         dbc.Input(id="bits-input", type="number", value=128, min=8, step=8)], width=3),
                dbc.Col([dbc.Button("🔄 Refresh All Systems", id="refresh-all", color="primary", className="mt-4")], width=2),
                dbc.Col([dbc.Button("📦 Capture 90B (raw)", id="capture-90b-btn", color="secondary", className="mt-4")], width=2),
                dbc.Col([dcc.Graph(id="entropy-gauge", figure=create_entropy_gauge(), config=GRAPH_CONFIG)], width=2),
            ]),
            dbc.Row([
                dbc.Col([html.Div(id="entropy-90b-card")], width=6),
                dbc.Col([html.Div(id="sustainability-card")], width=6),
            ])
        ])
    ], className="mb-4"),

    # QKD and AI anomaly
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5("🔐 Quantum Key Distribution", className="mb-0")],
                               style={"backgroundColor": "#06D6A0", "color": "white"}),
                dbc.CardBody([
                    html.P("E91 Protocol (Defense)", className="fw-bold"),
                    dbc.ButtonGroup([
                        dbc.Button("Run E91 Protocol", id="e91-btn", color="success", size="sm"),
                        dbc.Button("Bell Test", id="bell-test-btn", color="warning", size="sm"),
                    ], className="mb-2"),
                    html.Div(id="qkd-results"),
                    dcc.Graph(id="qkd-graph", figure=go.Figure(), config=GRAPH_CONFIG),
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.H5("🤖 AI Anomaly Detection", className="mb-0")],
                               style={"backgroundColor": "#457B9D", "color": "white"}),
                dbc.CardBody([
                    html.P("QRNG-Powered Intelligence", className="fw-bold"),
                    dbc.Button("Analyze Quantum Patterns", id="anomaly-btn", color="info", size="sm", className="mb-2"),
                    html.Div(id="anomaly-results"),
                    dcc.Graph(id="anomaly-graph", figure=go.Figure(), config=GRAPH_CONFIG),
                ])
            ])
        ], width=6),
    ], className="mb-4"),

    # Circuit visualizer
    dbc.Card([
        dbc.CardHeader([html.H5("🔧 Quantum Circuit Visualizer", className="mb-0")],
                       style={"backgroundColor": "#1D3557", "color": "white"}),
        dbc.CardBody([
            html.P("Basic QRNG: superposition (H) + measurement (M) to generate random bits", className="fw-bold"),
            dbc.Button("Show Circuit & Sample", id="circuit-btn", color="secondary", size="sm", className="mb-2"),
            html.Pre(id="circuit-ascii", style={"whiteSpace": "pre-wrap"}),
            html.Div(id="circuit-bits")
        ])
    ], className="mb-4"),

    # Defense platform status + sustainability
    dbc.Card([
        dbc.CardHeader([html.H4("🛡️ Defense Platform Status (QRNG-Secured)", className="mb-0")],
                       style={"backgroundColor": "#1D3557", "color": "white"}),
        dbc.CardBody([
            html.Div(id="defense-status-table"),
            dbc.Row([
                dbc.Col([dcc.Graph(id="performance-comparison", config=GRAPH_CONFIG)], width=6),
                dbc.Col([
                    html.H6("Sustainability (Scope 2)", className="text-success"),
                    html.P("Report CO₂e using location- and market-based emission factors."),
                    dbc.Row([
                        dbc.Col([dbc.Input(id="inp-kwh", type="number", step=0.001, placeholder="kWh measured")], width=4),
                        dbc.Col([dbc.Input(id="inp-ef-loc", type="number", step=0.0001, placeholder="EF loc (kg/kWh)")], width=4),
                        dbc.Col([dbc.Input(id="inp-ef-mkt", type="number", step=0.0001, placeholder="EF mkt (kg/kWh)")], width=4),
                    ], className="mb-2"),
                    dbc.Button("Update Sustainability Report", id="btn-sustain", color="success", size="sm"),
                    html.Div(id="sustainability-report-output", className="mt-2")
                ], width=6),
            ])
        ])
    ], className="mb-4"),

    # Crypto demo
    dbc.Card([
        dbc.CardHeader([html.H5("🔒 Quantum-Secured Communications Demo", className="mb-0")],
                       style={"backgroundColor": "#F4A261", "color": "white"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([dbc.Input(id="message-input", placeholder="Enter classified message...",
                                   value="OPERATION QUANTUM SHIELD: Secure channel established")], width=8),
                dbc.Col([dbc.ButtonGroup([
                    dbc.Button("🔐 Set QRNG Key", id="set-key-btn", color="warning", size="sm"),
                    dbc.Button("🔒 Encrypt", id="encrypt-btn", color="success", size="sm"),
                    dbc.Button("🔓 Decrypt", id="decrypt-btn", color="info", size="sm"),
                ])], width=4),
            ], className="mb-3"),
            html.Div(id="crypto-demo-results"),
        ])
    ], className="mb-4"),
])

# ---------------- Callbacks ----------------
@app.callback(Output("page-root","className"), Input("theme-store","data"))
def page_bg(theme):
    return "theme-dark" if (theme or "light") == "dark" else "theme-light"

@app.callback(Output("theme-store","data"), Input("toggle-theme","n_clicks"), State("theme-store","data"))
def toggle_theme(n, current):
    if not n:
        return current or "light"
    return "dark" if (current or "light") == "light" else "light"

@app.callback(
    [Output("qrng-demo-graph", "figure"),
     Output("qrng-output", "children"),
     Output("entropy-gauge", "figure"),
     Output("performance-comparison", "figure"),
     Output("qrng-header", "style"),
     Output("title-color", "style"),
     Output("entropy-90b-card", "children")],
    [Input("generate-qrng-btn", "n_clicks"),
     Input("interval-component", "n_intervals"),
     Input("capture-90b-btn", "n_clicks"),
     Input("theme-store","data")],
    [State("shots-input", "value"),
     State("bits-input", "value")]
)
def update_qrng_foundation(n_clicks, n_intervals, cap_clicks, theme, shots, num_bits):
    template, accent = theme_settings(theme)
    title_style = {"color": accent, "font-weight": "bold"}
    header_style = {"backgroundColor": accent}
    # Capture on demand
    ctx = callback_context
    if ctx.triggered and getattr(ctx, "triggered_id", None) == "capture-90b-btn":
        _ = make_api_call("/entropy/90b/capture", method="POST", json={"kind":"raw","samples":1000000})
    # Normal update
    if not n_clicks and n_intervals == 0:
        return (create_qrng_demo_figure(template, accent),
                "Click 'Generate Quantum Random Bits' to start",
                create_entropy_gauge(), create_performance_comparison(template, accent),
                header_style, title_style,
                dbc.Card(dbc.CardBody([html.P("90B Health: pending")]), color="light", outline=True))
    data = make_api_call(f"/rng?shots={shots}&bits={num_bits}")
    if "error" in data:
        return (create_qrng_demo_figure(template, accent),
                f"Error: {data['error']}",
                create_entropy_gauge(), create_performance_comparison(template, accent),
                header_style, title_style,
                dbc.Card(dbc.CardBody([html.P("90B Health: error")]), color="danger", outline=True))
    entropy = data.get("entropy", 0.95); entropy_history.append(entropy)
    bits = data.get("bits", "")
    # Bits figure
    if bits:
        x = list(range(len(bits))); y = [int(b) for b in bits]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers+lines", name="Quantum Random Bits",
                                 marker=dict(size=8, color=accent),
                                 line=dict(width=2, color=COLORS["quantum_glow"])))
        fig = set_transparent(fig.update_layout(
            title=f"Generated {len(bits)} Quantum Random Bits",
            xaxis_title="Bit Position", yaxis_title="Bit Value", height=300,
            yaxis=dict(tickvals=[0, 1], range=[-0.1, 1.1])
        ), template)
    else:
        fig = create_qrng_demo_figure(template, accent)

    q = data.get("randomness_quality", {}); env = data.get("environmental_impact", {})
    h = data.get("online_health", {}) or {}
    output = dbc.Card(dbc.CardBody([
        html.H6("✅ Quantum Random Bits Generated", className="text-success"),
        dbc.Row([
            dbc.Col([
                html.P(f"🎲 Bits: {bits[:64]}{'...' if len(bits) > 64 else ''}"),
                html.P(f"📊 Entropy: {entropy:.4f} (max: 1.0)"),
                html.P(f"🛡️ Defense Grade: {'✅ YES' if q.get('defense_grade') else '❌ NO'}"),
            ], width=6),
            dbc.Col([
                html.P(f"⚡ Energy Saved: {max(0.0, env.get('energy_saved_kwh', 0.0)):.4f} kWh"),
                html.P(f"🌱 CO₂ Reduced: {max(0.0, env.get('co2_reduced_kg', 0.0)):.4f} kg"),
                html.P(f"🚀 Applications: {3}"),
            ], width=6),
        ])
    ]), color="success", outline=True)

    health_card = dbc.Card(dbc.CardBody([
        html.H6("SP 800-90B Online Health", className="text-info"),
        html.P(f"Status: {'OK' if h.get('ok') else 'ALERT'}"),
        html.P(f"Reason: {h.get('reason','')}"),
        html.P(f"RCT Cutoff: {h.get('rct_cutoff')} | AP Window: {h.get('ap_window')} | AP Cutoff: {h.get('ap_cutoff')}"),
        html.H6("Datasets:"),
        html.P(f"raw: {make_api_call('/entropy/90b/status').get('datasets',{}).get('raw')}"),
        html.P(f"cond: {make_api_call('/entropy/90b/status').get('datasets',{}).get('cond')}"),
        html.P(f"restart: {make_api_call('/entropy/90b/status').get('datasets',{}).get('restart')}"),
    ]), color="info", outline=True)

    return fig, output, create_entropy_gauge(entropy), create_performance_comparison(template, accent), header_style, title_style, health_card

@app.callback(
    [Output("qkd-results", "children"),
     Output("qkd-graph", "figure")],
    [Input("e91-btn", "n_clicks"),
     Input("bell-test-btn", "n_clicks"),
     Input("theme-store","data")],
    [State("shots-input", "value")]
)
def update_qkd_protocols(e91_clicks, bell_clicks, theme, shots):
    template, accent = theme_settings(theme)
    ctx = callback_context
    if not ctx.triggered:
        return "Select a protocol to demonstrate quantum key distribution", go.Figure()
    button_id = getattr(ctx, "triggered_id", None) or ctx.triggered["prop_id"].split(".")
    if button_id == "e91-btn" and e91_clicks:
        data = make_api_call(f"/qkd?protocol=e91&shots={shots}")
        if "error" in data:
            return f"Error: {data['error']}", go.Figure()
        qber = float(data.get("qber", 0.0)); qber_history.append(qber)
        card = dbc.Card(dbc.CardBody([
            html.H6("🔐 E91 Protocol Results", className="text-success"),
            html.P(f"Key Length: {data.get('key_length', 0)} bits"),
            html.P(f"QBER: {qber:.3f} (threshold: 0.11)"),
            html.P(f"Status: {'🟢 SECURE' if data.get('secure') else '🔴 COMPROMISED'}"),
            html.P(f"Efficiency: {data.get('efficiency', 0):.3f}"),
        ]), color="success", outline=True)
        fig = go.Figure()
        fig.add_bar(x=["QBER"], y=[qber], name="QBER", marker_color=COLORS["warning"])
        fig.add_shape(type="line", x0=-0.5, x1=0.5, y0=0.11, y1=0.11,
                      line=dict(color=COLORS["danger"], width=2, dash="dash"))
        return card, set_transparent(fig.update_layout(title="E91 QBER vs Threshold (0.11)", height=250, yaxis_title="QBER"), template)
    if button_id == "bell-test-btn" and bell_clicks:
        data = make_api_call(f"/e91/chsh?shots={shots}")
        if "error" in data:
            return f"Error: {data['error']}", go.Figure()
        raw = data.get("correlations", {}) or {"E(a,b)": 0.0, "E(a,b')": 0.0, "E(a',b)": 0.0, "E(a',b')": 0.0}
        corr = {str(k): float(v) for k, v in raw.items()}
        fig = go.Figure(data=[go.Bar(x=list(corr.keys()), y=list(corr.values()), marker_color=accent)])
        fig = set_transparent(fig.update_layout(title="Bell Test Correlations", yaxis_title="Correlation Value", height=250), template)
        card = dbc.Card(dbc.CardBody([
            html.H6("🔔 Bell Inequality Test", className="text-warning"),
            html.P(f"S Parameter: {float(data.get('S_parameter', 0)):.3f}  |  CI95: {data.get('S_ci95')}"),
            html.P(f"Bell Violation: {'✅ YES' if data.get('bell_violation') else '❌ NO'}"),
            html.P(f"Alarm: {'⚠️' if data.get('alarm') else '—'}"),
        ]), color="warning", outline=True)
        return card, fig
    return "Select a protocol option", go.Figure()

@app.callback(
    Output("defense-status-table", "children"),
    [Input("interval-component", "n_intervals"),
     Input("theme-store","data")]
)
def update_defense_status(n_intervals, theme):
    data = make_api_call("/defense/status")
    if "error" in data:
        return html.P("Unable to load defense status")
    platforms = data.get("platforms", [])
    summary = data.get("summary", {})
    thead = [html.Thead([html.Tr([
        html.Th("Platform"), html.Th("Status"), html.Th("QRNG Enabled"),
        html.Th("Encryption"), html.Th("Entropy"), html.Th("Throughput"),
    ])])]
    rows = []
    for p in platforms:
        s_col = "success" if p["status"] == "Secure" else "warning"
        e_col = "success" if p.get("entropy_level", 0) > 0.9 else "warning"
        rows.append(html.Tr([
            html.Td([p.get("emoji", ""), " ", p["name"]]),
            html.Td(p["status"], className=f"text-{s_col}"),
            html.Td("✅ YES" if p.get("qrng_enabled") else "❌ NO"),
            html.Td(p.get("encryption", "Unknown")),
            html.Td(f"{p.get('entropy_level', 0):.3f}", className=f"text-{e_col}"),
            html.Td(p.get("throughput", "Unknown")),
        ]))
    table = dbc.Table(thead + [html.Tbody(rows)], bordered=True, hover=True, responsive=True)
    summary_card = dbc.Card(dbc.CardBody([
        html.H6("🛡️ Defense Network Summary", className="text-success"),
        html.P("🌟 QRNG Foundation: Active across all platforms"),
        html.P(f"📊 Security: {summary.get('security_percentage', 0):.1f}% platforms secure"),
        html.P(f"⚡ Avg Entropy: {summary.get('average_entropy', 0):.3f}"),
        html.P(f"🔐 Avg QBER: {summary.get('average_qber', 0):.3f}"),
    ]), color="success", outline=True, className="mb-3")
    return [summary_card, table]

@app.callback(
    [Output("anomaly-results", "children"), Output("anomaly-graph", "figure")],
    [Input("anomaly-btn", "n_clicks"),
     Input("interval-component", "n_intervals"),
     Input("theme-store","data")]
)
def run_anomaly(n_clicks, n_intervals, theme):
    template, accent = theme_settings(theme)
    if len(entropy_history) == 0 and len(qber_history) == 0:
        return "Collect data first (generate bits and/or run E91).", go.Figure()
    payload = {"entropy": list(entropy_history), "qber": list(qber_history)}
    res = make_api_call("/ai/anomaly", method="POST", json=payload)
    if "error" in res:
        return dbc.Alert(f"Anomaly service error: {res['error']}", color="danger"), go.Figure()
    card = dbc.Card(dbc.CardBody([
        html.H6("AI Anomaly Assessment", className="text-info"),
        html.P(f"Status: {res.get('status', 'UNKNOWN')}"),
        html.P(f"Alerts: {', '.join(res.get('alerts', [])) or 'None'}"),
        html.P(f"Entropy: {res.get('metrics',{}).get('entropy_level')}  |  QBER: {res.get('metrics',{}).get('qber_level')}"),
    ]), color="info", outline=True)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Entropy", "QBER"))
    if entropy_history:
        fig.add_bar(x=list(range(len(entropy_history))), y=list(entropy_history),
                    name="Entropy", marker_color=COLORS["success"], row=1, col=1)
    if qber_history:
        fig.add_bar(x=list(range(len(qber_history))), y=list(qber_history)),
        fig.add_bar(x=list(range(len(qber_history))), y=list(qber_history),
                    name="QBER", marker_color=COLORS["warning"], row=1, col=2)
    return card, set_transparent(fig.update_layout(height=300, showlegend=False), template)

@app.callback(
    [Output("crypto-demo-results", "children"),
     Output("crypto-store", "data")],
    [Input("set-key-btn", "n_clicks"),
     Input("encrypt-btn", "n_clicks"),
     Input("decrypt-btn", "n_clicks")],
    [State("message-input", "value"),
     State("crypto-store", "data")]
)
def crypto_demo(set_key_clicks, encrypt_clicks, decrypt_clicks, message, cstate):
    ctx = callback_context
    if not ctx.triggered:
        return "Use QRNG-derived keys: Set Key → Encrypt → Decrypt.", cstate
    button_id = getattr(ctx, "triggered_id", None) or ctx.triggered["prop_id"].split(".")
    if button_id == "set-key-btn" and set_key_clicks:
        key_data = make_api_call("/rng?bits=256&shots=4096")
        if "error" in key_data:
            return dbc.Alert(f"Key generation failed: {key_data['error']}", color="danger"), cstate
        set_result = make_api_call("/crypto/set_key", method="POST", json={"bitstring": key_data.get("bits", "")})
        if "error" in set_result:
            return dbc.Alert(f"Key setting failed: {set_result.get('reason', set_result['error'])}", color="danger"), cstate
        return dbc.Alert([html.H6("🔐 Quantum Key Set"),
                          html.P(f"Length: {set_result.get('key_length_bits', 0)} bits"),
                          html.P(f"Health: {'OK' if set_result.get('online_health',{}).get('ok') else 'ALERT'}")],
                         color="success"), {"nonce": None, "ciphertext": None}
    if button_id == "encrypt-btn" and encrypt_clicks:
        if not message:
            return dbc.Alert("Enter a message before encrypting.", color="warning"), cstate
        enc = make_api_call("/crypto/encrypt", method="POST", json={"message": message})
        if "error" in enc:
            return dbc.Alert(f"Encrypt error: {enc['error']}", color="danger"), cstate
        store = {"nonce": enc.get("nonce"), "ciphertext": enc.get("ciphertext")}
        card = dbc.Card(dbc.CardBody([
            html.H6("🟢 Encrypted (AES‑256‑GCM)"),
            html.P(f"Nonce (b64): {store['nonce']}"),
            html.P(f"Ciphertext (b64): {store['ciphertext']}"),
            html.P("Keep both for decryption."),
        ]), color="success", outline=True)
        return card, store
    if button_id == "decrypt-btn" and decrypt_clicks:
        if not cstate or not cstate.get("nonce") or not cstate.get("ciphertext"):
            return dbc.Alert("Nothing to decrypt: encrypt something first.", color="warning"), cstate
        dec = make_api_call("/crypto/decrypt", method="POST", json=cstate)
        if "error" in dec:
            return dbc.Alert(f"Decrypt error: {dec['error']}", color="danger"), cstate
        card = dbc.Card(dbc.CardBody([html.H6("🔓 Decrypted & Authenticated"), html.P(dec.get("message", ""))]),
                        color="info", outline=True)
        return card, cstate
    return "QRNG cryptography demo ready", cstate

@app.callback(
    [Output("circuit-ascii", "children"),
     Output("circuit-bits", "children")],
    Input("circuit-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_circuit(n):
    data = make_api_call("/qrng/circuit?shots=32")
    if "error" in data:
        return f"Error: {data['error']}", ""
    ascii_circ = data.get("ascii_circuit", "Circuit unavailable")
    bits = data.get("bits", "")
    zeros = bits.count("0"); ones = bits.count("1")
    return ascii_circ, f"Quantum Random Bits: {bits[:64]}{'...' if len(bits)>64 else ''} (0s: {zeros}, 1s: {ones})"

@app.callback(
    Output("sustainability-report-output", "children"),
    Input("btn-sustain", "n_clicks"),
    [State("inp-kwh", "value"), State("inp-ef-loc", "value"), State("inp-ef-mkt", "value")]
)
def update_sustainability_report(n, kwh, ef_loc, ef_mkt):
    if not n:
        s = requests.get(f"{BACKEND_URL}/sustainability/report", timeout=5).json()
        if "error" in s:
            return "No report"
        return f"kWh: {s.get('kwh',0.0)} | CO2e loc: {s.get('co2_loc')} kg | CO2e mkt: {s.get('co2_mkt')} kg"
    payload = {"window_start": "now", "window_end": "now", "kwh": kwh or 0.0,
               "ef_loc": ef_loc or 0.0, "ef_mkt": ef_mkt or 0.0}
    s = make_api_call("/sustainability/report", method="POST", json=payload)
    if "error" in s:
        return f"Error: {s['error']}"
    return f"kWh: {s.get('kwh',0.0)} | CO2e loc: {s.get('co2_loc')} kg | CO2e mkt: {s.get('co2_mkt')} kg"

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
