import plotly.express as px
from colors import colors


def deposited_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], font_color='white', xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), hovermode='x unified', font_size=20)
    return fig


def redeemed_over_time(df):
    df = df.sort_values(by="Date", ascending=True)
    df["Quantity"] = df["Quantity"].cumsum()
    fig = px.area(df, x="Date", y="Quantity")
    fig.update_layout(paper_bgcolor=colors['bg_color'], plot_bgcolor=colors['bg_color'], font_color='white', xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False), hovermode='x unified', font_size=20)
    return fig
