import imp
import dash
from dash import html, Input, Output
from dash import dcc

import pandas as pd
from subgrounds.subgrounds import to_dataframe
import datetime as dt
from helpers import (pct_change,drop_duplicates, date_manipulations, black_list_manipulations, 
                    region_manipulations, subsets)
from Figures import *
from subgrounds.subgrounds import Subgrounds
from data_related_constants import methodology_dict, rename_map
from colors import colors, fonts
# from get_data import execute
from import_data import get_data

df = get_data()

#rename_columns
df=df.rename(columns=rename_map)
#datetime manipulations
df = date_manipulations(df)
#Blacklist manipulations
df = black_list_manipulations(df)
#Region manipulations
df = region_manipulations(df)
#7 day and 30 day subsets 
sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)

#drop duplicates data for BCT calculations
df_carbon=drop_duplicates(df)

#Summary
total_toucan_credits = df['Quantity'].sum()
total_BCT = df_carbon['BCT Quantity'].sum()
sd_credits = sd_pool['Quantity'].sum()
sd_change = pct_change(last_sd_pool['Quantity'].sum(),sd_credits)
td_credits = td_pool['Quantity'].sum()
td_change = pct_change(last_td_pool['Quantity'].sum(),td_credits)

#Figures
#7-day-performance
fig_seven_day_plots = sub_plots(sd_pool,last_sd_pool,7)
fig_seven_day_map=map(sd_pool,7)
fig_seven_day_indicator=indicator_subsets(sd_pool,last_sd_pool,7)
#30-day-performance
fig_thirty_day_plots = sub_plots(td_pool,last_td_pool,30)
fig_thirty_day_map = map(td_pool,30)
fig_thirty_day_indicator=indicator_subsets(td_pool,last_td_pool,30)
#total
fig_total_indicator=indicator_total(df)
fig_total_plots = total_plots(df)
fig_total_map = total_map(df)
fig_total_region = region_volume_vs_date(df)
fig_total_metho = methodology_volume_vs_region(df)
fig_metho_description = methodology_table(methodology_dict)
fig_pool_pie_chart,fig_eligible_pool_pie_chart = pool_pie_chart(df_carbon)

# Dashboard
app = dash.Dash(__name__)

app.layout=html.Div([
  html.Div([
  html.H1("Toucan Carbon Credits Dashboard")]
  ,style ={'textAlign': 'center','padding-top':'96px','color':colors['kg_color'],'font-size':fonts['heading']}),


  html.Div([
  html.H1("Summary")]
  ,style ={'textAlign': 'center','padding-top':'96px','color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),

  html.Div([
    html.Div([dcc.Graph(figure=fig_total_indicator)],style ={'padding-top':'96px','padding-right':'120px','display':'inline-block'}),
    html.Div([dcc.Graph(figure=fig_seven_day_indicator)],style ={'padding-top':'96px','padding-right':'120px','display':'inline-block'}),
    html.Div([dcc.Graph(figure=fig_thirty_day_indicator)],style ={'padding-top':'96px','display':'inline-block'}),
  ],style ={'textAlign': 'center','width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
  

  html.Div([
        dcc.Dropdown(options=[{'label':'Last 7 Days Performance','value':'Last 7 Days Performance'},
        {'label':'Last 30 Days Performance','value':'Last 30 Days Performance'},
        {'label':'Overall Performance','value':'Overall Performance'}],value='Last 7 Days Performance',id='summary-type')
    ]),

  html.Div([
  html.H1(id="Last X Days")]
  ,style ={'textAlign': 'center','padding-top':'96px', 'color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),
  html.Div([dcc.Graph(id="sub plots")]),
  html.Div([dcc.Graph(id="map")],style={'padding-top':'96px'}),

  html.Div(id="fig_total_region",style={'padding-top':'96px'}),
  html.Div(id="fig_total_metho",style={'padding-top':'96px'}),
  html.Div(id="fig_metho_description"),

  html.Div([
  html.Div(id="fig_pool_pie_chart",style={'padding-top':'96px','display': 'inline-block'}),
  html.Div(id="fig_eligible_pool_pie_chart",style={'padding-top':'96px','display': 'inline-block'})
],style={'textAlign': 'center'})
],
style={'height':'100%','backgroundColor':colors['bg_color'],
      'margin':'0',
      'padding':'0'
        })

@app.callback(
    Output(component_id='Last X Days', component_property='children'),
    Output(component_id='sub plots', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id="fig_total_region", component_property='children'),
    Output(component_id="fig_total_metho", component_property='children'),
    Output(component_id="fig_metho_description", component_property='children'),
    Output(component_id='fig_pool_pie_chart', component_property='children'),
    Output(component_id='fig_eligible_pool_pie_chart', component_property='children'),
  
    
    Input(component_id='summary-type', component_property='value')
)
def update_output_div(input_value):
    if input_value=='Last 7 Days Performance':
      return "Last 7 Days Performance",fig_seven_day_plots,fig_seven_day_map,html.Br(),html.Br(),html.Br(),html.Br(),html.Br()
    elif input_value=='Last 30 Days Performance':
      return "Last 30 Days Performance",fig_thirty_day_plots,fig_thirty_day_map,html.Br(),html.Br(),html.Br(),html.Br(),html.Br()
    elif input_value=='Overall Performance':
      return "Overall Performance",fig_total_plots,fig_total_map,dcc.Graph(figure=fig_total_region) \
      ,dcc.Graph(figure=fig_total_metho),dcc.Graph(figure=fig_metho_description) \
        ,dcc.Graph(figure=fig_pool_pie_chart),dcc.Graph(figure=fig_eligible_pool_pie_chart)


fig_total_region = region_volume_vs_date(df)
fig_total_metho = methodology_volume_vs_region(df)
fig_metho_description = methodology_table(methodology_dict)
fig_pool_pie_chart,fig_eligible_pool_pie_chart = pool_pie_chart(df_carbon)
      


if __name__ == '__main__':
  app.run_server(debug=True)
