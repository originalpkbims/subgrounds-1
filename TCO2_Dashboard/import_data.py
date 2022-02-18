from subgrounds.subgrounds import to_dataframe
from subgrounds.subgrounds import Subgrounds

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
    carbon_offsets.balanceNCT,
    carbon_offsets.totalBridged,
    carbon_offsets.bridges.value,
    carbon_offsets.bridges.timestamp
    ])

    data = sg.execute(req)
    df_bridged = to_dataframe(data)

    carbon_offsets = carbon_data.Query.retires(
    first = 4999
    )

    req = sg.mk_request([
    carbon_offsets.value,
    carbon_offsets.timestamp,
    carbon_offsets.offset.tokenAddress,
    carbon_offsets.offset.region,
    carbon_offsets.offset.vintage,
    carbon_offsets.offset.projectID,
    carbon_offsets.offset.standard,
    carbon_offsets.offset.methodology,
    carbon_offsets.offset.standard,
    carbon_offsets.offset.totalRetired,
    ])

    data = sg.execute(req)
    df_retired = to_dataframe(data)
    
    return df_bridged, df_retired
