import imp
from multiprocessing import pool
from pydoc import classname
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
from data_related_constants import methodology_dict, rename_map, retires_rename_map
from colors import colors, fonts
# from get_data import execute
from import_data import get_data

df, df_retired = get_data()

#rename_columns
df=df.rename(columns=rename_map)
df_retired=df_retired.rename(columns=retires_rename_map)
#datetime manipulations
df = date_manipulations(df)
df_retired=date_manipulations(df_retired)
#Blacklist manipulations
df = black_list_manipulations(df)
df_retired=black_list_manipulations(df_retired)
#Region manipulations
df = region_manipulations(df)
df = region_manipulations(df)
#7 day and 30 day subsets 
sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)
sd_pool_retired, last_sd_pool_retired, td_pool_retired, last_td_pool_retired = subsets(df_retired)

#drop duplicates data for Carbon Pool calculations
df_carbon=drop_duplicates(df)

# #Summary
# total_toucan_credits = df['Quantity'].sum()
# sd_credits = sd_pool['Quantity'].sum()
# sd_change = pct_change(last_sd_pool['Quantity'].sum(),sd_credits)
# td_credits = td_pool['Quantity'].sum()
# td_change = pct_change(last_td_pool['Quantity'].sum(),td_credits)

#Summary
fig_total_indicator_bridged=indicator_total(df)
fig_total_indicator_retired=indicator_total(df_retired)


#Figures
#7-day-performance
fig_seven_day_volume = sub_plots_volume(sd_pool,last_sd_pool,7)
fig_seven_day_vintage = sub_plots_vintage(sd_pool,last_sd_pool,7)
fig_seven_day_map=map(sd_pool,7)
# fig_seven_day_indicator=indicator_subsets(sd_pool,last_sd_pool,7)
#30-day-performance
fig_thirty_day_volume = sub_plots_volume(td_pool,last_td_pool,30)
fig_thirty_day_vintage = sub_plots_vintage(td_pool,last_td_pool,30)
fig_thirty_day_map = map(td_pool,30)
fig_thirty_day_indicator=indicator_subsets(td_pool,last_td_pool,30)
#total
# fig_total_indicator=indicator_total(df_retired)
fig_total_volume = total_volume(df)
fig_total_vintage = total_vintage(df)
fig_total_map = total_map(df)
fig_total_region = region_volume_vs_date(df)
fig_total_metho = methodology_volume_vs_region(df)
# fig_metho_description = methodology_table(methodology_dict)
fig_pool_pie_chart = pool_pie_chart(df_carbon)

# Dashboard
app = dash.Dash(__name__)

app.layout=html.Div([
  html.Div([
  html.H1("Toucan Carbon Credits Dashboard")]
  ,style ={'text-align':'center','padding-top':'96px','color':colors['kg_color'],'font-size':fonts['heading']},className="row"),

  html.Div([
  html.H1("Summary")]
  ,style ={'textAlign': 'center','padding-top':'96px','color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),

  html.Div([
    html.Div([],className='col'),
    html.Div([dcc.Graph(figure=fig_total_indicator_bridged)],className='col-3'),
    html.Div([dcc.Graph(figure=fig_total_indicator_retired)],style ={'display':'inline-block'},className='col-3'),
    html.Div([dcc.Graph(figure=fig_thirty_day_indicator)],style ={'display':'inline-block'},className='col-3'),
    html.Div([],className='col'),
  ],className="row",style = {'padding-top':'96px'}),
  
  html.Div([
  html.Div([],className='col-10'),
  html.Div([
      dcc.Dropdown(options=[{'label':'BCT','value':'BCT'},
      {'label':'NCT','value':'NCT'}],value='BCT',id='pie-chart-summary',placeholder='Select Carbon Pool')
  ],className='col-1'),
  ],className='row',style = {'padding-top':'96px'}),
  html.Div([
    html.Div([],className='col'),
    html.Div(dcc.Graph(figure=fig_pool_pie_chart),className='col-4'),
    html.Div([dcc.Graph(id="eligible pie chart plot")],className='col-4'),
    html.Div([],className='col'),
  ],className='row'),

  html.Div([
  html.Div([],className='col-2'),
  html.Div([
      dcc.Dropdown(options=[{'label':'Last 7 Days Performance','value':'Last 7 Days Performance'},
      {'label':'Last 30 Days Performance','value':'Last 30 Days Performance'},
      {'label':'Overall Performance','value':'Overall Performance'}],value='Last 7 Days Performance',id='summary-type',placeholder='Select Summary Type')
  ],className='col-4')],className='row',style = {'padding-top':'96px'}),

  html.Div([
  html.H1(id="Last X Days")]
  ,style ={'textAlign': 'center','padding-top':'96px', 'color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),
  
  html.Div([
  html.Div([],className='col'),
  html.Div([dcc.Graph(id="volume plot")],className='col-5'),
  html.Div([dcc.Graph(id="vintage plot")],className='col-5'),
  html.Div([],className='col')
  ],className='row'),

  html.Div([
  html.Div([],className='col'),
  html.Div([dcc.Graph(id="map")],className='col-8'),
  html.Div([],className='col')
 ],className='row',style={'padding-top':'96px'}),

  html.Div([
  html.Div([],className='col'),
  html.Div(id="fig_total_region",className='col-8'),
  html.Div([],className='col')
 ],className='row',style={'padding-top':'96px'}),


  html.Div([
  html.Div([],className='col'),
  html.Div(id="fig_total_metho",className='col-8'),
  html.Div([],className='col')
 ],className='row',style={'padding-top':'96px'}),
  # html.Div(id="fig_metho_description"),
  html.Div([],style={'padding-top':'96px'})
],
style={'height':'100%','backgroundColor':'#121212',
      'margin':'0',
      'padding':'0'
        })

@app.callback(
    Output(component_id='Last X Days', component_property='children'),
    Output(component_id='volume plot', component_property='figure'),
    Output(component_id='vintage plot', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id="fig_total_region", component_property='children'),
    Output(component_id="fig_total_metho", component_property='children'),
    # Output(component_id="fig_metho_description", component_property='children'),
  
    
    Input(component_id='summary-type', component_property='value')
)
def update_output_div(input_value):
    if input_value=='Last 7 Days Performance':
      return "Last 7 Days Performance",fig_seven_day_volume,fig_seven_day_vintage,fig_seven_day_map,html.Br(),html.Br()
    elif input_value=='Last 30 Days Performance':
      return "Last 30 Days Performance",fig_thirty_day_volume,fig_thirty_day_vintage,fig_thirty_day_map,html.Br(),html.Br()
    elif input_value=='Overall Performance':
      return "Overall Performance",fig_total_volume,fig_total_vintage,fig_total_map,dcc.Graph(figure=fig_total_region) \
      ,dcc.Graph(figure=fig_total_metho)

@app.callback(
    Output(component_id='eligible pie chart plot', component_property='figure'),
    Input(component_id='pie-chart-summary', component_property='value')
)
def update_eligible_pie_chart(pool_key):
      fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon,pool_key)
      return fig_eligible_pool_pie_chart
      


if __name__ == '__main__':
  app.run_server(port=4455,debug=True)
