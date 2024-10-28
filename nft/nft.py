

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output,State,ALL
import sqlite3

#全体のレイアウト。呼び出される場所
def nft_layout(params):
  '''
  return html.Div(
    [
      up,
      html.Hr(),
      down
      ]
    )
    '''
  return html.Div([
    html.H1('NFT Page'),
    html.Div(f'pid: {params.get("pid", "N/A")}'),
    html.Div(f'nid: {params.get("nid", "N/A")}')
        # ここにnftページのコンテンツを追加
  ])

  

