import unittest

from subgrounds.query import Argument, DataRequest, Document, InputValue, Query, Selection
from subgrounds.schema import TypeMeta, TypeRef
from subgrounds.transform import LocalSyntheticField, TypeTransform, chain_transforms, transform_response, transform_data_type, transform_request


class TestTransform(unittest.TestCase):
  def test_transform_request1(self):
    expected = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, None, [
            Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
          ])
        ])
      )
    ])

    fmeta = TypeMeta.FieldMeta('price1', '', [], TypeRef.non_null('Float'))

    req = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, None, [
            Selection(TypeMeta.FieldMeta('price1', '', [], TypeRef.Named('Float')), None, None, None),
          ])
        ])
      )
    ])

    replacement = [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
    ]

    new_query = transform_request(fmeta, replacement, req)

    self.assertEqual(new_query, expected)

  def test_transform_response1(self):
    expected = [{
      'price1': 0.5,
      'amount0In': 0.0,
      'amount0Out': 10.0,
      'amount1In': 20.0,
      'amount1Out': 0.0
    }]

    data = [{
      'amount0In': 0.0,
      'amount0Out': 10.0,
      'amount1In': 20.0,
      'amount1Out': 0.0
    }]

    fmeta = TypeMeta.FieldMeta('price1', '', [], TypeRef.non_null('Float'))

    def f(in0, out0, in1, out1):
      return abs(in0 - out0) / abs(in1 - out1)

    arg_select = [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
    ]

    req = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('price1', '', [], TypeRef.Named('Float')), None, None, None)
        ])
      )
    ])

    transformed_data = transform_response(fmeta, f, arg_select, req, data)

    self.assertEqual(transformed_data, expected)

  def test_transform_response2(self):
    expected = [{
      'swap': {
        'price1': 0.5,
        'amount0In': 0.0,
        'amount0Out': 10.0,
        'amount1In': 20.0,
        'amount1Out': 0.0
      }
    }]

    data = [{
      'swap': {
        'amount0In': 0.0,
        'amount0Out': 10.0,
        'amount1In': 20.0,
        'amount1Out': 0.0
      }
    }]

    fmeta = TypeMeta.FieldMeta('price1', '', [], TypeRef.non_null('Float'))

    def f(in0, out0, in1, out1):
      return abs(in0 - out0) / abs(in1 - out1)

    arg_select = [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
    ]

    req = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('swap', '', [], TypeRef.Named('Swap')), None, None, [
            Selection(TypeMeta.FieldMeta('price1', '', [], TypeRef.Named('Float')), None, None, None),
          ])
        ])
      )
    ])

    transformed_data = transform_response(fmeta, f, arg_select, req, data)

    self.assertEqual(transformed_data, expected)

  def test_transform_response3(self):
    expected = [{
      'swaps': [{
        'price1': 0.5,
        'amount0In': 0.0,
        'amount0Out': 10.0,
        'amount1In': 20.0,
        'amount1Out': 0.0
      }]
    }]

    data = [{
      'swaps': [{
        'amount0In': 0.0,
        'amount0Out': 10.0,
        'amount1In': 20.0,
        'amount1Out': 0.0
      }]
    }]

    def f(in0, out0, in1, out1):
      return abs(in0 - out0) / abs(in1 - out1)

    arg_select = [
      Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
      Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
    ]

    fmeta = TypeMeta.FieldMeta('price1', '', [], TypeRef.non_null('Float'))

    req = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, None, [
            Selection(TypeMeta.FieldMeta('price1', '', [], TypeRef.Named('Float')), None, None, None),
          ])
        ])
      )
    ])

    transformed_data = transform_response(fmeta, f, arg_select, req, data)

    self.assertEqual(transformed_data, expected)

  def test_transform_response4(self):
    expected = [{
      'pair': {
        'token0Symbol': 'USDC',
        'token0': {
          'symbol': 'USDC'
        }
      }
    }]

    data = [{
      'pair': {
        'token0': {
          'symbol': 'USDC'
        }
      }
    }]

    fmeta = TypeMeta.FieldMeta('token0Symbol', '', [], TypeRef.non_null('String'))

    def f(x):
      return x

    arg_select = [
      Selection(TypeMeta.FieldMeta('token0', '', [], TypeRef.Named('Token')), None, None, [
        Selection(TypeMeta.FieldMeta('symbol', '', [], TypeRef.non_null('String')))
      ])
    ]

    query = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('pair', '', [], TypeRef.Named('Pair')), None, None, [
            Selection(TypeMeta.FieldMeta('token0Symbol', '', [], TypeRef.Named('String')), None, None, None),
          ])
        ])
      )
    ])

    transformed_data = transform_response(fmeta, f, arg_select, query, data)

    self.assertEqual(transformed_data, expected)

  def test_transform_data_type1(self):
    expected = [{
      'swaps': [{
        'amount0In': 0.0,
        'amount0Out': 10.0,
        'amount1In': 20.0,
        'amount1Out': 0.0
      }]
    }]

    data = [{
      'swaps': [{
        'amount0In': '0.0',
        'amount0Out': '10.0',
        'amount1In': '20.0',
        'amount1Out': '0.0'
      }]
    }]

    def f(bigdecimal):
      return float(bigdecimal)

    query = DataRequest(documents=[
      Document(
        'abc',
        Query(None, [
          Selection(TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')), None, None, [
            Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
          ])
        ])
      )
    ])

    type_ = TypeRef.Named('BigDecimal')

    transformed_data = transform_data_type(type_, f, query, data)

    self.assertEqual(transformed_data, expected)


class TestQueryTransform(unittest.TestCase):
  def test_roundtrip1(self):
    expected = [{
      'swaps': [{
        'amount0In': 0.25,
        'amount0Out': 0.0,
        'amount1In': 0.0,
        'amount1Out': 89820.904371079570860909
      }]
    }]

    transform = TypeTransform(TypeRef.Named('BigDecimal'), lambda bigdecimal: float(bigdecimal))

    req = DataRequest(documents=[
      Document(
        'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
        Query(None, [
          Selection(
            TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')),
            None,
            [
              Argument('first', InputValue.Int(1)),
              Argument('orderBy', InputValue.Enum('timestamp')),
              Argument('orderDirection', InputValue.Enum('desc')),
              Argument('where', InputValue.Object({
                'timestamp_lt': InputValue.Int(1638554700)
              }))
            ],
            [
              Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
              Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
              Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
              Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
            ]
          )
        ])
      )
    ])

    data = chain_transforms([transform], req)

    self.assertEqual(data, expected)

  def test_roundtrip2(self):
    expected = [{
      'swaps': [{
        'price0': 359283.61748431827,
        'amount0In': 0.25,
        'amount0Out': 0.0,
        'amount1In': 0.0,
        'amount1Out': 89820.904371079570860909
      }]
    }]

    transforms = [
      LocalSyntheticField(
        None,
        TypeMeta.FieldMeta('price0', '', [], TypeRef.non_null('Float')),
        lambda in0, out0, in1, out1: abs(in1 - out1) / abs(in0 - out0),
        [
          Selection(TypeMeta.FieldMeta('amount0In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
          Selection(TypeMeta.FieldMeta('amount0Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
          Selection(TypeMeta.FieldMeta('amount1In', '', [], TypeRef.Named('BigDecimal')), None, None, None),
          Selection(TypeMeta.FieldMeta('amount1Out', '', [], TypeRef.Named('BigDecimal')), None, None, None),
        ]
      ),
      TypeTransform(TypeRef.Named('BigDecimal'), lambda bigdecimal: float(bigdecimal))
    ]

    query = Query(None, [
      Selection(
        TypeMeta.FieldMeta('swaps', '', [], TypeRef.non_null_list('Swap')),
        None,
        [
          Argument('first', InputValue.Int(1)),
          Argument('orderBy', InputValue.Enum('timestamp')),
          Argument('orderDirection', InputValue.Enum('desc')),
          Argument('where', InputValue.Object({
            'timestamp_lt': InputValue.Int(1638554700)
          }))
        ],
        [
          Selection(TypeMeta.FieldMeta('price0', '', [], TypeRef.Named('Float')), None, None, None)
        ]
      )
    ])

    req = DataRequest(documents=[
      Document(url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2', query=query)
    ])

    data = chain_transforms(transforms, req)

    self.assertEqual(data, expected)
