from click import style
import pandas as pd
import dash
from dash import html
from dash import dcc

from subgrounds.subgrounds import to_dataframe
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from collections import defaultdict
from helpers import add_px_figure 
from plotly.subplots import make_subplots
from colors import colors

app = dash.Dash(__name__)

app.layout=html.Div([
    html.H1("Hi",style={'height':'100%','min-height': '100%','top':'0px',
  'left':'0px','backgroundColor':colors['bg_color'],
      'margin':'0px',
      'padding':'0px'
        })])


if __name__ == '__main__':
  app.run_server(debug=True)