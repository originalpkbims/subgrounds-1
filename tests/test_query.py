import unittest

from subgrounds.query import Argument, DataRequest, Document, Query, Selection, InputValue, VariableDefinition
from subgrounds.schema import TypeMeta, TypeRef
from subgrounds.subgraph import Subgraph, SyntheticField
from subgrounds.subgrounds import Subgrounds

from tests.utils import schema


class TestQueryString(unittest.TestCase):
  def setUp(self):
    self.schema = schema()
    self.subgraph = Subgraph("", self.schema)

  def tearDown(self) -> None:
    SyntheticField.counter = 0

  def test_graphql_1(self):
    expected = """query {
  pairs(first: 100, where: {reserveUSD_lt: "10.0"}, orderBy: reserveUSD, orderDirection: desc) {
    id
    token0 {
      name
      symbol
    }
    token1 {
      name
      symbol
    }
  }
}"""

    query = Query(None, [
      Selection(
        TypeMeta.FieldMeta('pairs', '', [
          TypeMeta.ArgumentMeta('first', '', TypeRef.Named('Int'), None),
          TypeMeta.ArgumentMeta('where', '', TypeRef.Named('Pair_filter'), None),
          TypeMeta.ArgumentMeta('orderBy', '', TypeRef.Named('Pair_orderBy'), None),
          TypeMeta.ArgumentMeta('orderDirection', '', TypeRef.Named('OrderDirection'), None),
        ], TypeRef.non_null_list('Pair')),
        arguments=[
          Argument('first', InputValue.Int(100)),
          Argument('where', InputValue.Object({'reserveUSD_lt': InputValue.String('10.0')})),
          Argument('orderBy', InputValue.Enum('reserveUSD')),
          Argument('orderDirection', InputValue.Enum('desc'))
        ],
        selection=[
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String'))),
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), selection=[
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String'))),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')))
          ]),
          Selection(TypeMeta.FieldMeta('token1', '', [], TypeRef.Named('Token')), selection=[
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String'))),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')))
          ])
        ]
      )
    ])

    self.assertEqual(query.graphql, expected)

  def test_graphql_2(self):
    expected = """query {
  xab8f96f0e14a4db3: pairs(first: 100, where: {reserveUSD_lt: "10.0"}, orderBy: reserveUSD, orderDirection: desc) {
    id
    token0 {
      name
      symbol
    }
    token1 {
      name
      symbol
    }
  }
}"""

    app = Subgrounds()

    pairs = self.subgraph.Query.pairs(
      first=100,
      where=[
        self.subgraph.Pair.reserveUSD < 10
      ],
      orderBy=self.subgraph.Pair.reserveUSD,
      orderDirection='desc'
    )

    req = app.mk_request([
      pairs.id,
      pairs.token0.name,
      pairs.token0.symbol,
      pairs.token1.name,
      pairs.token1.symbol,
    ])

    self.assertEqual(req.documents[0].query.graphql, expected)

  def test_graphql_3(self):
    expected = """query($tokenId: String!) {
  token(id: $tokenId) {
    id
    name
    symbol
  }
}"""

    query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('token', '', [], TypeRef.non_null_list('Token')), None, [Argument('id', InputValue.Variable('tokenId'))], [
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ],
      [
        VariableDefinition('tokenId', TypeRef.non_null('String'))
      ]
    )

    self.assertEqual(query.graphql, expected)


# class TestExecution(unittest.TestCase):
#   def test_execute_1(self):
#     expected = [
#       {
#         'token': [
#           {
#             'id': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
#             'name': 'USD//C',
#             'symbol': 'USDC'
#           },
#           {
#             'id': '0x6b175474e89094c44da98b954eedeac495271d0f',
#             'name': 'Dai Stablecoin',
#             'symbol': 'DAI'
#           }
#         ]
#       }
#     ]

#     req = DataRequest(documents=[
#       Document(
#         'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
#         Query(None, [
#           Selection(
#             TypeMeta.FieldMeta('token', '', [], TypeRef.non_null_list('Token')),
#             None,
#             [
#               Argument('id', InputValue.Variable('tokenId')),
#             ],
#             [
#               Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
#               Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
#               Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
#             ]
#           )
#         ], [VariableDefinition('tokenId', TypeRef.non_null('String'))]),
#         variables=[
#           {'tokenId': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'},
#           {'tokenId': '0x6b175474e89094c44da98b954eedeac495271d0f'}
#         ]
#       )
#     ])

#     self.assertEqual(execute(req), expected)


class TestSelectionFunctions(unittest.TestCase):
  def test_add_selection_1(self):
    expected = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    og_selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    new_selection = Selection.add_selection(
      og_selection,
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], [])
    )

    self.assertEqual(new_selection, expected)

  def test_add_selection_2(self):
    expected = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    og_selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    new_selection = Selection.add_selection(
      og_selection,
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    )

    self.assertEqual(new_selection, expected)

  def test_add_selections_1(self):
    expected = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
    ])

    og_selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    new_selection = Selection.add_selections(
      og_selection,
      [
        Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
        Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
      ]
    )

    self.assertEqual(new_selection, expected)

  def test_remove_selection_1(self):
    expected = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    og_selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
    ])

    new_selection = Selection.remove_selection(
      og_selection,
      Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
    )

    self.assertEqual(new_selection, expected)

  def test_remove_selection_2(self):
    expected = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    og_selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    new_selection = Selection.remove_selection(
      og_selection,
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    )

    self.assertEqual(new_selection, expected)

  def test_remove_selection_3(self):
    expected = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [])

    og_selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    new_selection = Selection.remove_selection(
      og_selection,
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [])
    )

    self.assertEqual(new_selection, expected)

  def test_contains_1(self):
    selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    s2 = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    self.assertEqual(Selection.contains(selection, s2), True)

  def test_contains_2(self):
    selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    s2 = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    self.assertEqual(Selection.contains(selection, s2), False)

  def test_contains_3(self):
    selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [
      Argument('first', InputValue.Int(100)),
    ], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    s2 = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    self.assertEqual(Selection.contains(selection, s2), True)

  def test_contains_4(self):
    selection = Selection(fmeta=TypeMeta.FieldMeta(name='log', description='', arguments=[], type_=TypeRef.Named(name_='String')), alias=None, arguments=[], selection=[])

    s2 = Selection(fmeta=TypeMeta.FieldMeta(name='log', description='', arguments=[], type_=TypeRef.Named(name_='String')), alias=None, arguments=[], selection=[])

    self.assertEqual(Selection.contains(selection, s2), True)

  def test_select_1(self):
    expected = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    selection = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    s2 = Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
    ])

    self.assertEqual(Selection.select(selection, s2), expected)

  def test_select_2(self):
    expected = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    s2 = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [])
    ])

    self.assertEqual(Selection.select(selection, s2), expected)

  def test_consolidate_1(self):
    expected = [
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    ]

    selections = [
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    ]

    self.assertEqual(Selection.consolidate(selections), expected)

  def test_consolidate_2(self):
    expected = [
      Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    ]

    selections = [
      Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ]),
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    ]

    self.assertEqual(Selection.consolidate(selections), expected)


class TestQueryFunctions(unittest.TestCase):
  def test_add_selection_1(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    og_query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    new_query = Query.add_selection(
      og_query,
      Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
        Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], [])
      ])
    )

    self.assertEqual(new_query, expected)

  def test_add_selection_2(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    og_query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    new_query = Query.add_selection(
      og_query,
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    )

    self.assertEqual(new_query, expected)

  def test_add_selections_1(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
        ])
      ],
      []
    )

    og_query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    new_query = Query.add_selections(
      og_query,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
        ])
      ]
    )

    self.assertEqual(new_query, expected)

  def test_remove_selection_1(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    og_query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
        ])
      ],
      []
    )

    new_query = Query.remove_selection(
      og_query,
      Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
        Selection(TypeMeta.FieldMeta('timestamp', '', [], TypeRef.Named('Int')), None, [], []),
      ])
    )

    self.assertEqual(new_query, expected)

  def test_remove_selection_2(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    og_query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    new_query = Query.remove_selection(
      og_query,
      Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
        Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
          Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
          Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
        ])
      ])
    )

    self.assertEqual(new_query, expected)

  def test_select_1(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    selection = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    s2 = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, [], [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('Float')), None, [], []),
        ])
      ],
      []
    )

    self.assertEqual(Query.select(selection, s2), expected)

  def test_select_2(self):
    expected = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    selection = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    s2 = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [])
        ])
      ],
      []
    )

    self.assertEqual(Query.select(selection, s2), expected)

  def test_contains_1(self):
    query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    q = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [])
        ])
      ],
      []
    )

    self.assertEqual(Query.contains(query, q), True)

  def test_contains_2(self):
    query = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    q = Query(
      None,
      [
        Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
          Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
            Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
            Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
          ])
        ])
      ],
      []
    )

    self.assertEqual(Query.contains(query, q), True)


class TestContainsList(unittest.TestCase):
  def test_contains_list_1(self):
    selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    self.assertEqual(selection.contains_list(), True)

  def test_contains_list_2(self):
    selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.non_null_list('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.non_null_list('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    self.assertEqual(selection.contains_list(), True)

  def test_contains_list_3(self):
    selection = Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.Named('Pair')), None, [], [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, [], [
        Selection(TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('name', '', [], TypeRef.Named('String')), None, [], []),
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.Named('String')), None, [], []),
      ])
    ])

    self.assertEqual(selection.contains_list(), False)