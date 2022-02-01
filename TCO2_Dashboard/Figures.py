
from distutils.errors import CCompilerError
from re import template
# from tkinter import _Padding, font
from unicodedata import name
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

from subgrounds.subgrounds import Subgrounds

def sub_plots(sd_pool,last_sd_pool,num):
    fig = make_subplots(
        rows=2, 
        cols=2,
        specs=[[{"type":"domain"}, {"type":"domain"}],[{"type":"xy"}, {"type":"xy"}]],
        subplot_titles=("", "", "Tokenization Volumes By Day", f"Distribution of Vintages ({num}d)"),
        vertical_spacing=0.1,
        )
    
    
    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = sum(sd_pool['Quantity']),
        title=dict(text =f"Credits tokenized ({num}d)"),
        number = dict(suffix = " tCO2"),
        delta = {'position': "bottom", 'reference': sum(last_sd_pool['Quantity']), 'relative':True, 'valueformat':'.1%'},
        domain = {'x': [0, .5], 'y': [0.6, 1]}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = np.average(sd_pool['Vintage'],weights=sd_pool['Quantity']),
        number = dict(valueformat= ".1f"),
        delta = {"reference": np.average(last_sd_pool['Vintage'],weights=last_sd_pool['Quantity']), "valueformat": ".1f"},
        title=dict(text =f"Average Credit Vintage ({num}d)"),
        domain = {'x': [.5,1],'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            sd_pool.groupby("Bridging Date")['Quantity'].sum().reset_index(), 
            x="Bridging Date", 
            y="Quantity", 
            title="Tokenization Volumes By Day",
            ),
        fig,
        row=2, col=1)
    
    
    add_px_figure(
        px.bar(
            sd_pool.groupby('Vintage')['Quantity'].sum().to_frame().reset_index(), 
            x='Vintage', 
            y='Quantity', 
            title=f'Distribution of Vintages ({num}d)'
            ),
        fig,
        row=2, col=2
    )
    fig.update_layout(height=600,paper_bgcolor=colors['bg_color'])
    return fig
 
def map(df,num):
    
    country_index = defaultdict(str,{country:pycountry.countries.search_fuzzy(country)[0].alpha_3 for country in df.Region.astype(str).unique() if country!='nan'})
    country_volumes = df.groupby('Region')['Quantity'].sum().sort_values(ascending=False).to_frame().reset_index()
    country_volumes['Country Code'] = [country_index[country] for country in country_volumes['Region']]
    fig = px.choropleth(country_volumes, locations="Country Code",
                    color="Quantity",
                    hover_name='Region',
                    color_continuous_scale = px.colors.sequential.Plasma,
                    height=600)
    
    fig.update_layout(title=dict(
    text=f'Where have the past {num}-day credits originated from?',
    x=0.5,
    font=dict(
        color=colors['kg_color_sub2'],
        size=fonts['figure']
    )),
    font_color='white',dragmode=False,paper_bgcolor=colors['bg_color'])
    return fig


def total_plots(sd_pool):
    fig = make_subplots(
        rows=2, 
        cols=2,
        specs=[[{"type":"domain"}, {"type":"domain"}],[{"type":"xy"}, {"type":"xy"}]],
        vertical_spacing=0.1,
        subplot_titles=("", "", "Tokenization Volumes By Day", "Distribution of Vintages")
        )
    fig.update_layout(font_color='white')

    fig.add_trace(go.Indicator(
        mode = "number",
        value = sum(sd_pool['Quantity']),
        title=dict(text ="Credits tokenized (total)"),
        number = dict(suffix = " tCO2"),
        domain = {'x': [0, .5], 'y': [0.6, 1]}))

    fig.add_trace(go.Indicator(
        mode = "number",
        value = np.average(sd_pool['Vintage'],weights=sd_pool['Quantity']),
        number = dict(valueformat= ".1f"),
        title=dict(text ="Average Credit Vintage (total)"),
        domain = {'x': [.5,1],'y': [0.6, 1]}))

    add_px_figure(
        px.bar(
            sd_pool.groupby("Bridging Date")['Quantity'].sum().reset_index(), 
            x="Bridging Date", 
            y="Quantity", 
            title="Tokenization Volumes By Day"
            ),
        fig,
        row=2, col=1)

    add_px_figure(
        px.bar(
            sd_pool.groupby('Vintage')['Quantity'].sum().to_frame().reset_index(), 
            x='Vintage', 
            y='Quantity', 
            title=f'Distribution of Vintages (total)'
            ),
        fig,
        row=2, col=2
    )

    fig.update_layout(height=600,paper_bgcolor=colors['bg_color'])
    return fig


def total_map(df):
    
    country_index = defaultdict(str,{country:pycountry.countries.search_fuzzy(country)[0].alpha_3 for country in df.Region.astype(str).unique() if country!='nan'})
    country_volumes = df.groupby('Region')['Quantity'].sum().sort_values(ascending=False).to_frame().reset_index()
    country_volumes['Country Code'] = [country_index[country] for country in country_volumes['Region']]
    fig = px.choropleth(country_volumes, locations="Country Code",
                    color="Quantity",
                    hover_name='Region',
                    color_continuous_scale = px.colors.sequential.Plasma,
                    height=600)

    fig.update_layout(title=dict(text="Where have all the past credits originated from?",
    x=0.5,font=dict(color=colors['kg_color_sub2'],size=fonts['figure'])),
    font_color='white',dragmode=False,paper_bgcolor=colors['bg_color'])
    return fig

def region_volume_vs_date(df):
    #List of Regions
    lst_reg = list(df["Region"].value_counts().index[:])

    #Create Indicator and Quantity Columns
    for i in lst_reg:
        df[i+'_ind'] = 0
        df.loc[df["Region"]==i,i+'_ind'] = 1
        df[i+"_Quantity"] = df["Quantity"] * df[i+'_ind']

    #Grouby weekly
    #line chart - based off weekly
    lst_reg_Quantity = [i+"_Quantity" for i in lst_reg]
    qty_vs_date = df.groupby('Bridging Date')[["Quantity"] + lst_reg_Quantity].sum().reset_index()
    qty_vs_date = qty_vs_date.sort_values(by='Bridging Date')
    qty_vs_date["Bridging Date"]=pd.to_datetime(qty_vs_date["Bridging Date"])
    qty_vs_date=qty_vs_date.resample('W',on='Bridging Date')[["Quantity"] + lst_reg_Quantity].sum().reset_index()

    #Region_Quantity vs Time
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=qty_vs_date['Bridging Date'],y=qty_vs_date['Quantity'],name="Volume"))
    for i in lst_reg_Quantity:
        fig.add_trace(go.Bar(x=qty_vs_date['Bridging Date'],y=qty_vs_date[i],name=i.replace("_Quantity","")))

    fig.update_layout(title=dict(text="What is the trend of Tokenized Credits Volume (Weekly)? <br> Which Regions' carbon credits are consistently tokenized? <br> Which Regions' carbon credits are recently tokenized?",
    x=0.5,y=0.95,font=dict(color=colors['kg_color_sub2'],size=fonts['figure'])),font_color='white',
                        xaxis_title = 'Date',
                        yaxis_title = 'Volume',
                    barmode='stack',
                    paper_bgcolor=colors['bg_color']
                )
    return fig

def methodology_volume_vs_region(df):
    #List of Regions
    lst_metho = list(df["Methodology"].value_counts().index[:])

    #Create Indicator and Quantity Columns
    for i in lst_metho:
        df[i+'_ind'] = 0
        df.loc[df["Methodology"]==i,i+'_ind'] = 1
        df[i+"_Quantity"] = df["Quantity"] * df[i+'_ind']

    lst_metho_Quantity = [i+"_Quantity" for i in lst_metho]
    qty_vs_region = df.groupby('Region')[["Quantity"] + lst_metho_Quantity].sum().reset_index()

    #Methodology_Quantity vs Region
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=qty_vs_region['Region'],y=qty_vs_region['Quantity'],name="Volume",textfont=dict(color='red')))
    for i in lst_metho_Quantity:
        fig.add_trace(go.Bar(x=qty_vs_region['Region'],y=qty_vs_region[i],name=i.replace("_Quantity","")))

    fig.update_layout(title=dict(text="Methodology Distribution with respect to Region",
    x=0.5,font=dict(color=colors['kg_color_sub2'],size=fonts['figure'])),font_color='white',
                        xaxis_title = 'Region',
                        yaxis_title = 'Volume',
                        barmode='stack',
                        paper_bgcolor=colors['bg_color'])

    return fig


def methodology_table(metho_dict):
    fig=go.Figure(data = [go.Table(header = dict(values=['Methodology','Methodology Description']),
    cells=dict(values=[list(metho_dict.keys()),list(metho_dict.values())]))])
    
    fig.update_layout(title=dict(
        text='Methodology Brief Description',
        x=0.5,
        font=dict(
            color=colors['kg_color_sub2'],size=20
        )),
        paper_bgcolor=colors['bg_color'])



    return fig
