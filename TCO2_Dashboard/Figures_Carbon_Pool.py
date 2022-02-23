import pandas as pd
from subgrounds.subgrounds import to_dataframe
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pycountry
from collections import defaultdict
from helpers import add_px_figure 
from plotly.subplots import make_subplots
from colors import colors, fonts
from itertools import cycle

from subgrounds.subgrounds import Subgrounds


def deposited_over_time(df):
    df = df.sort_values(by="Date",ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(paper_bgcolor=colors['bg_color'],plot_bgcolor=colors['bg_color'],font_color='white',xaxis=dict(showgrid=False),
              yaxis=dict(showgrid=False),hovermode='x unified')
    return fig

def redeemed_over_time(df):
    df = df.sort_values(by="Date",ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(paper_bgcolor=colors['bg_color'],plot_bgcolor=colors['bg_color'],font_color='white',xaxis=dict(showgrid=False),
              yaxis=dict(showgrid=False),hovermode='x unified')
    return fig