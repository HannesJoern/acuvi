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


app = dash.Dash(server=server, routes_pathname_prefix="/dash/")

with open('/home/hannes/Desktop/acuvi-repo/acuvi/data.csv', 'r', newline='') as f:
    rd = csv.reader(f, delimiter = ',')
    for row in rd:
        norm_factor = float(row[0])
        rise_fac = float(row[1])
        fall_fac = float(row[2])
        exponent = float(row[3])
        upper_part = float(row[4])
        lower_part = float(row[5])
    f.close()
    
app.layout = html.Div([
    html.H6("Ideal brightness"),
    dcc.Slider(
        id="slider_brightness",
        min=0,
        max=1,
        step = 0.01,
        value = norm_factor
    ),
    html.Br(),

    html.H6("Temporal smoothing for going up"),
    dcc.Slider(
        id="slider_rise",
        min=0.5,
        max=1,
        step = 0.01,
        value = rise_fac
    ),
    html.Br(),
    html.H6("temporal smoothing for going down"),
    dcc.Slider(
        id="slider_fall",
        min=0.5,
        max=0.95,
        step = 0.01,
        value = fall_fac
    ),
    html.Br(),
    html.H6("exponent"),
    dcc.Slider(
        id="slider_exponent",
        min=1,
        max=10,
        step = 1,
        value = exponent
    ),
    html.Br(),
    html.H6("upper half (%)"),
    dcc.Slider(
        id="slider_upper",
        min=0,
        max=1,
        step = 0.1,
        value = upper_part
    ),
    html.Br(),
    html.H6("lower half (%)"),
    dcc.Slider(
        id="slider_lower",
        min=0,
        max=1,
        step = 0.1,
        value = lower_part
    ),
    html.Br(),
    html.P(id="output")
    
])


@app.callback([Output("output", 'children')],[Input("slider_brightness", 'value'), Input("slider_rise", 'value'), Input("slider_fall", 'value'), Input("slider_exponent", 'value'), Input("slider_upper", 'value'), Input("slider_lower", 'value')])
def write_data(input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower):
    for i in range(100):
        try:
            with open("/home/hannes/Desktop/acuvi-repo/acuvi/data.csv", 'w+', newline='') as f:
                write = csv.writer(f)
                write.writerow([input_brightness, input_rise, input_fall, input_exponent, input_upper, input_lower])
            return ["Written with brightness " + str(input_brightness) +" rise fac " + str(input_rise) + " fall fac " + str( input_fall) + " exponent " + str(input_exponent) + " upper " + str(input_upper) + " lower " + str(input_lower)]
        except:
            print("couldnt write file")
    return ["error"]
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port= 8008, debug=True)