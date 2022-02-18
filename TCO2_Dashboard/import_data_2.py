from subgrounds.subgrounds import to_dataframe
from subgrounds.subgrounds import Subgrounds

def get_data():
                      
    sg = Subgrounds()
    carbon_data = sg.load_subgraph('https://api.thegraph.com/subgraphs/name/cujowolf/polygon-bridged-carbon')

    carbon_offsets = carbon_data.Query.retires(
    # orderBy=carbon_data.CarbonOffset.lastUpdate,
    # orderDirection='desc',
    first = 10
    )

    req = sg.mk_request([
    carbon_offsets.value,
    # carbon_offsets.region,
    # carbon_offsets.vintage,
    # carbon_offsets.projectID,
    # carbon_offsets.standard,
    # carbon_offsets.methodology,
    # carbon_offsets.balanceBCT,
    # carbon_offsets.balanceNCT,
    # carbon_offsets.totalBridged,
    # carbon_offsets.retirements.value,
    # carbon_offsets.bridges.timestamp
    ])

    data = sg.execute(req)
    df = to_dataframe(data)
    
    return df

df = get_data()
print(df)