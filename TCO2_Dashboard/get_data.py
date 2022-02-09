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
from data_related_constants import methodology_dict, rename_map, rename_map_carbon
from colors import colors, fonts

def execute():
                      
    sg = Subgrounds()
    carbon_data = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    bridges = carbon_data.Query.bridges(
    orderBy=carbon_data.Bridge.timestamp,
    orderDirection='desc',
    first = 4999
    )

    req = sg.mk_request([
    bridges.value,
    bridges.timestamp,
    bridges.offset.region,
    bridges.offset.vintage,
    bridges.offset.projectID,
    bridges.offset.standard,
    bridges.offset.methodology,
    bridges.offset.tokenAddress,
    bridges.offset.balanceBCT
    ])

    data = sg.execute(req)
    df = to_dataframe(data)

    carbon_offsets = carbon_data.Query.carbonOffsets(
    orderBy=carbon_data.CarbonOffset.lastUpdate,
    orderDirection='desc',
    first = 4999
    )

    req = sg.mk_request([
    carbon_offsets.tokenAddress,
    carbon_offsets.region,
    carbon_offsets.balanceBCT,
    carbon_offsets.totalBridged,
    ])

    data = sg.execute(req)
    df_carbon = to_dataframe(data)
    
    return df,df_carbon
