import dash
from dash import html
from dash import dcc
import flask
import csv
from dash.dependencies import Input, Output, State
import numpy as np

server = flask.Flask(__name__)


@server.route("/")
def home():
    return "Hello, Flask!"

settings = np.array([0, 0, 0], dtype = np.float)
app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

app.layout = html.Div([
    html.H6("Ideal brightness"),
    dcc.Slider(
        id="slider_brightness",
        min=0,
        max=1,
        step = 0.01,
        value = 0.5
    ),
    html.Br(),

    html.H6("Temporal smoothing for going up"),
    dcc.Slider(
        id="slider_rise",
        min=0,
        max=1,
        step = 0.01,
        value = 0.5
    ),
    html.Br(),
    html.H6("temporal smoothing for going down"),
    dcc.Slider(
        id="slider_fall",
        min=0,
        max=1,
        step = 0.01,
        value = 0.5
    ),
    html.Br(),
    html.H6("exponent"),
    dcc.Slider(
        id="slider_exponent",
        min=1,
        max=4,
        step = 1,
        value = 2
    ),
    html.Br(),
    html.H6("upper half (%)"),
    dcc.Slider(
        id="slider_upper",
        min=0,
        max=1,
        step = 0.01,
        value = 1
    ),
    html.Br(),
    html.H6("lower half (%)"),
    dcc.Slider(
        id="slider_lower",
        min=0,
        max=1,
        step = 0.01,
        value = 1
    ),
    html.Br(),
    html.P(id="output")
    
])


@app.callback([Output("output", 'children')],[Input("slider_brightness", 'value'), Input("slider_rise", 'value'), Input("slider_fall", 'value'), Input("slider_exponent", 'value'), Input("slider_upper", 'value'), Input("slider_lower", 'value')])
def write_data(input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower):
    for i in range(100):
        try:
            with open("data.csv", 'w+', newline='') as f:
                write = csv.writer(f)
                write.writerow([input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower])
            return ["Written with brightness " + str(input_brightness) +" rise fac " + str(input_rise) + " fall fac " + str( input_fall) + " exponent " + str(input_exponent) + " upper " + str(input_upper) + " lower " + str(input_lower)]
        except:
            print("couldnt write file")
    return ["error"]
if __name__ == "__main__":
    app.run_server(debug=True)
