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
df_retired = region_manipulations(df_retired)
#7 day and 30 day subsets 
sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)
sd_pool_retired, last_sd_pool_retired, td_pool_retired, last_td_pool_retired = subsets(df_retired)

#drop duplicates data for Carbon Pool calculations
df_carbon=drop_duplicates(df)

#Summary
fig_total_indicator_bridged=indicator_total(df,None,"Total Bridged TCO2",False)
fig_total_indicator_retired=indicator_total(df_retired,None,"Total Retired TCO2",False)
fig_total_indicator_current=indicator_total(df,df_retired,"Current Supply",True)
fig_pool_pie_chart = pool_pie_chart(df_carbon)

#Figures
#7-day-performance
fig_seven_day_volume = sub_plots_volume(sd_pool,last_sd_pool,title_indicator="Credits Bridged (7d)",title_graph="Distribution of Volume (7d)")
fig_seven_day_volume_retired = sub_plots_volume(sd_pool_retired,last_sd_pool_retired,"Credits Retired (7d)","Distribution of Volume (7d)")
fig_seven_day_vintage = sub_plots_vintage(sd_pool,last_sd_pool,"Average Credit Vintage (7d)","Distribution of Vintages (7d)")
fig_seven_day_vintage_retired = sub_plots_vintage(sd_pool_retired,last_sd_pool_retired,"Average Credit Vintage (7d)","Distribution of Vintages (7d)")
fig_seven_day_map=map(sd_pool,'Where have the past 7-day credits originated from?')
fig_seven_day_map_retired=map(sd_pool_retired,'Where were the past 7-day retired credits originated from?')

#30-day-performance
fig_thirty_day_volume  = sub_plots_volume(td_pool,last_td_pool,"Credits Bridged (30d)","Distribution of Volume (30d)")
fig_thirty_day_volume_retired = sub_plots_volume(td_pool_retired,last_td_pool_retired,"Credits Retired (30d)","Distribution of Volume (30d)")
fig_thirty_day_vintage = sub_plots_vintage(td_pool,last_td_pool,"Average Credit Vintage (7d)","Distribution of Vintages (30d)")
fig_thirty_day_vintage_retired = sub_plots_vintage(td_pool_retired,last_td_pool_retired,"Average Credit Vintage (30d)","Distribution of Vintages (30d)")
fig_thirty_day_map = map(td_pool,'Where have the past 30-day credits originated from?')
fig_thirty_day_map_retired = map(td_pool_retired,'Where were the past 30-day retired credits originated from?')

#Total
fig_total_volume = total_volume(df)
fig_total_volume_retired = total_volume(df_retired)
fig_total_vintage = total_vintage(df)
fig_total_vintage_retired = total_vintage(df_retired)
fig_total_map = map(df,'Where have all the past credits originated from?')
fig_total_map_retired = map(df_retired,'Where were all the past retired credits originated from?')
fig_total_region = region_volume_vs_date(df,"What is the trend of Tokenized Credits Volume (Weekly)? <br> Which Regions' carbon credits are consistently tokenized?")
fig_total_region_retired = region_volume_vs_date(df_retired,"What is the trend of Retired Credits Volume (Weekly)? <br> Which Regions' carbon credits are consistently retired?")
fig_total_metho = methodology_volume_vs_region(df)
fig_total_metho_retired = methodology_volume_vs_region(df_retired)


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
    html.Div([dcc.Graph(figure=fig_total_indicator_current)],style ={'display':'inline-block'},className='col-3'),
    html.Div([],className='col'),
  ],className="row",style = {'padding-top':'96px'}),
  
  html.Div([
  html.Div([],className='col-10'),
  html.Div([
      dcc.Dropdown(options=[{'label':'BCT','value':'BCT'},
      {'label':'NCT','value':'NCT'}],value='BCT',id='pie_chart_summary',placeholder='Select Carbon Pool')
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
      {'label':'Overall Performance','value':'Overall Performance'}],value='Overall Performance',id='summary_type',placeholder='Select Summary Type')
  ],className='col-4'),
  html.Div([
      dcc.Dropdown(options=[{'label':'Bridged','value':'Bridged'},
      {'label':'Retired','value':'Retired'}],value='Bridged',id='bridged_or_retired',placeholder='Select Summary Type')
  ],className='col-4')]
  ,className='row',style = {'padding-top':'96px'}),

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
    Input(component_id='summary_type', component_property='value'),
    Input(component_id='bridged_or_retired', component_property='value')
)
def update_output_div(summary_type,TCO2_type):
    if summary_type=='Last 7 Days Performance':
      if TCO2_type == 'Bridged':
        return "Last 7 Days Performance",fig_seven_day_volume,fig_seven_day_vintage,fig_seven_day_map,html.Br(),html.Br()
      elif TCO2_type == 'Retired':
        return "Last 7 Days Performance",fig_seven_day_volume_retired,fig_seven_day_vintage_retired,fig_seven_day_map_retired,html.Br(),html.Br()
    
    elif summary_type=='Last 30 Days Performance':
      if TCO2_type == 'Bridged':
        return "Last 30 Days Performance",fig_thirty_day_volume,fig_thirty_day_vintage,fig_thirty_day_map,html.Br(),html.Br()
      elif TCO2_type == 'Retired':
        return "Last 30 Days Performance",fig_thirty_day_volume_retired,fig_thirty_day_vintage_retired,fig_thirty_day_map_retired,html.Br(),html.Br()
    
    elif summary_type=='Overall Performance':
      if TCO2_type == 'Bridged':
        return "Overall Performance",fig_total_volume,fig_total_vintage,fig_total_map,dcc.Graph(figure=fig_total_region) \
        ,dcc.Graph(figure=fig_total_metho)
      elif TCO2_type =='Retired':
        return "Overall Performance",fig_total_volume_retired,fig_total_vintage_retired,fig_total_map_retired,dcc.Graph(figure=fig_total_region_retired) \
        ,dcc.Graph(figure=fig_total_metho_retired)

@app.callback(
    Output(component_id='eligible pie chart plot', component_property='figure'),
    Input(component_id='pie_chart_summary', component_property='value')
)
def update_eligible_pie_chart(pool_key):
      fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon,pool_key)
      return fig_eligible_pool_pie_chart
      


if __name__ == '__main__':
  app.run_server(port=4455,debug=True)
