
from subgrounds.subgrounds import Subgrounds



def get_data_2():
    sg = Subgrounds()
    carbon_data = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.carbonOffsets(
    orderBy=carbon_data.CarbonOffset.lastUpdate,
    orderDirection='desc',
    first = 4999
    )

    req = sg.query_df([
    carbon_offsets.tokenAddress,
        carbon_offsets.region,
        carbon_offsets.vintage,
        carbon_offsets.projectID,
        carbon_offsets.standard,
        carbon_offsets.methodology,
        carbon_offsets.balanceBCT,
        # carbon_offsets.balanceNCT,
        carbon_offsets.totalBridged,
        carbon_offsets.retirements.value
    ])

    # data = sg.execute(req)
    
    # df = to_dataframe(data)
    # print(df)
    return req
