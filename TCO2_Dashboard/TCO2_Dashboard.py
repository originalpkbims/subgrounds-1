
import dash
from dash import html
from dash import dcc

import pandas as pd
from subgrounds.subgrounds import to_dataframe
import datetime as dt
from helpers import (pct_change, date_manipulations, black_list_manipulations, 
                    region_manipulations, subsets)
from Figures import *
from subgrounds.subgrounds import Subgrounds
from data_related_constants import methodology_dict, rename_map
from colors import colors, fonts

sg = Subgrounds()
carbon_data = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

bridges = carbon_data.Query.bridges(
  orderBy=carbon_data.Bridge.timestamp,
  orderDirection='desc',
)

req = sg.mk_request([
  bridges.value,
  bridges.timestamp,
  bridges.offset.region,
  bridges.offset.vintage,
  bridges.offset.projectID,
  bridges.offset.standard,
  bridges.offset.methodology,
  bridges.offset.tokenAddress
])

data = sg.execute(req)
df = to_dataframe(data)

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

#Summary
total_toucan_credits = df['Quantity'].sum()
sd_credits = sd_pool['Quantity'].sum()
sd_change = pct_change(last_sd_pool['Quantity'].sum(),sd_credits)
td_credits = td_pool['Quantity'].sum()
td_change = pct_change(last_td_pool['Quantity'].sum(),td_credits)

#Figures
#7-day-performance
fig_seven_day_plots = sub_plots(sd_pool,last_sd_pool,7)
fig_seven_day_map=map(sd_pool,7)
#30-day-performance
fig_thirty_day_plots = sub_plots(td_pool,last_td_pool,30)
fig_thirty_day_map = map(td_pool,30)
#total
fig_total_plots = total_plots(df)
fig_total_map = total_map(df)
fig_total_region = region_volume_vs_date(df)
fig_total_metho = methodology_volume_vs_region(df)
fig_metho_description = methodology_table(methodology_dict)


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
  html.H2(f"There are {total_toucan_credits:,} Verra registry credits that have been tokenized by Toucan")]
  ,style ={'textAlign': 'center','color':'white','font-size':fonts['summary']}),
  html.Div([
  html.H2(f"The past 7 days has seen {sd_credits:,} credits get tokenized ({round(sd_change,1)}% change from last week)")]
  ,style ={'textAlign': 'center','color':'white','font-size':fonts['summary']}),
  html.Div([
  html.H2(f"The last 30 days has seen {td_credits:,} credits get tokenized ({round(td_change,1)}% change from previous 30 days)")]
  ,style ={'textAlign': 'center','color':'white','font-size':fonts['summary']}),

  html.Div([
  html.H1("Last 7 Days Performance")]
  ,style ={'textAlign': 'center','padding-top':'96px', 'color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),
  html.Div([dcc.Graph(figure=fig_seven_day_plots)]),
  html.Div([dcc.Graph(figure=fig_seven_day_map)],style={'padding-top':'96px'}),

html.Div([
  html.H1("Last 30 Days Performance")]
  ,style ={'textAlign': 'center','padding-top':'96px', 'color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),
  html.Div([dcc.Graph(figure=fig_thirty_day_plots)]),
  html.Div([dcc.Graph(figure=fig_thirty_day_map)],style={'padding-top':'96px'}),

html.Div([
  html.H1("Overall Performance")]
  ,style ={'textAlign': 'center','padding-top':'96px', 'color':colors['kg_color_sub'],'font-size':fonts['sub_heading']}),
  
  html.Div([dcc.Graph(figure=fig_total_plots)]),
  html.Div([dcc.Graph(figure=fig_total_map)],style={'padding-top':'96px'}),

  html.Div([dcc.Graph(figure=fig_total_region)],style={'padding-top':'96px'}),
  
  html.Div([dcc.Graph(figure=fig_total_metho)],style={'padding-top':'96px'}),
  html.Div([dcc.Graph(figure=fig_metho_description)])
],
style={'height':'100%','backgroundColor':colors['bg_color'],
      'margin':'0',
      'padding':'0'
        
        })

if __name__ == '__main__':
  app.run_server(debug=True)
