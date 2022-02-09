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

def get_data():
                      
    sg = Subgrounds()
    carbon_data = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.carbonOffsets(
    orderBy=carbon_data.CarbonOffset.lastUpdate,
    orderDirection='desc',
    first = 4999
    )

    req = sg.mk_request([
    carbon_offsets.tokenAddress,
    carbon_offsets.region,
    carbon_offsets.vintage,
    carbon_offsets.projectID,
    carbon_offsets.standard,
    carbon_offsets.methodology,
    carbon_offsets.balanceBCT,
    carbon_offsets.totalBridged,
    carbon_offsets.bridges.value,
    carbon_offsets.bridges.timestamp
    ])

    data = sg.execute(req)
    df = to_dataframe(data)
    
    return df
