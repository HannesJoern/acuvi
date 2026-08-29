"""A small Dash/Flask web UI for live-tuning the visualizer while it runs.

Sliders here write their values to data.csv, which visualizer.py polls and reloads
periodically. This lets you adjust brightness, smoothing, and gain in real time without
restarting the main acuvi process - useful for dialing in the look at a live event.

Run with: python server.py
Then open http://<host>:8008/dash/ in a browser.
"""

import csv
import os

import dash
import flask
from dash import dcc, html
from dash.dependencies import Input, Output

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")

server = flask.Flask(__name__)


@server.route("/")
def home():
    return "acuvi tuning server is running. Open /dash/ for the controls."


app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

with open(CONFIG_PATH, 'r', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    norm_factor, rise_fac, fall_fac, exponent, upper_part, lower_part = (float(x) for x in next(reader))

app.layout = html.Div([
    html.H6("Ideal brightness"),
    dcc.Slider(id="slider_brightness", min=0, max=1, step=0.01, value=norm_factor),
    html.Br(),

    html.H6("Temporal smoothing for going up"),
    dcc.Slider(id="slider_rise", min=0.5, max=1, step=0.01, value=rise_fac),
    html.Br(),

    html.H6("Temporal smoothing for going down"),
    dcc.Slider(id="slider_fall", min=0.5, max=0.95, step=0.01, value=fall_fac),
    html.Br(),

    html.H6("Exponent"),
    dcc.Slider(id="slider_exponent", min=1, max=10, step=1, value=exponent),
    html.Br(),

    html.H6("Upper half (%)"),
    dcc.Slider(id="slider_upper", min=0, max=1, step=0.1, value=upper_part),
    html.Br(),

    html.H6("Lower half (%)"),
    dcc.Slider(id="slider_lower", min=0, max=1, step=0.1, value=lower_part),
    html.Br(),

    html.P(id="output"),
])


@app.callback(
    [Output("output", 'children')],
    [
        Input("slider_brightness", 'value'),
        Input("slider_rise", 'value'),
        Input("slider_fall", 'value'),
        Input("slider_exponent", 'value'),
        Input("slider_upper", 'value'),
        Input("slider_lower", 'value'),
    ],
)
def write_data(input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower):
    """Persist the current slider values to data.csv so the running visualizer can pick them up."""
    try:
        with open(CONFIG_PATH, 'w+', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower])
        return [
            f"Written with brightness {input_brightness}, rise fac {input_rise}, "
            f"fall fac {input_fall}, exponent {input_exponent}, "
            f"upper {input_upper}, lower {input_lower}"
        ]
    except OSError as e:
        return [f"error writing config: {e}"]


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8008, debug=True)
