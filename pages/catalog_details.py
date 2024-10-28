import dash_bootstrap_components as dbc
from dash import html, dcc

from pages.qa import split_text
from .core import catalog_db, write_db

def generate_cost_section(a_formula, b_formula, c_formula):
    # 説明メッセージ
    explanation_message = (
        "この非機能テストにかかるコストは、以下の３つの式の和で算出されます。"
        "A(準備コスト) + B(実施コスト) + C(分析コスト)"
    )
    
    # A, B, Cがデータベースから取得されているかチェック
    if a_formula and b_formula and c_formula:
        # A, B, Cがある場合のメッセージと式の表示
        return dbc.Card(
            [
                dbc.CardHeader(html.H4("コスト算出"),style={"textAlign": "center"}),
                dbc.CardBody(
                    [
                        # 説明メッセージ
                        dbc.Alert(explanation_message, color="info", className="mb-4"),
                        
                        # Aコスト
                        html.Div(
                            [
                                html.H5("A: 準備コスト", className="text-primary"),
                                html.Div(
                                    [
                                        html.Small("式:", style={"fontSize": "18px", "marginRight": "8px"}),
                                        html.Span(f"{a_formula}", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}),
                                    ],
                                    style={
                                        "backgroundColor": "#f8f9fa",
                                        "border": "1px solid #dee2e6",
                                        "padding": "10px",
                                        "borderRadius": "5px",
                                        "boxShadow": "0px 2px 8px rgba(0, 0, 0, 0.1)"
                                    },
                                    className="mb-4"
                                )
                            ]
                        ),

                        # Bコスト
                        html.Div(
                            [
                                html.H5("B: 実施コスト", className="text-primary"),
                                html.Div(
                                    [
                                        html.Small("式:", style={"fontSize": "18px", "marginRight": "8px"}),
                                        html.Span(f"{b_formula}", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}),
                                    ],
                                    style={
                                        "backgroundColor": "#f8f9fa",
                                        "border": "1px solid #dee2e6",
                                        "padding": "10px",
                                        "borderRadius": "5px",
                                        "boxShadow": "0px 2px 8px rgba(0, 0, 0, 0.1)"
                                    },
                                    className="mb-4"
                                )
                            ]
                        ),

                        # Cコスト
                        html.Div(
                            [
                                html.H5("C: 分析コスト", className="text-primary"),
                                html.Div(
                                    [
                                        html.Small("式:", style={"fontSize": "18px", "marginRight": "8px"}),
                                        html.Span(f"{c_formula}", style={"fontSize": "26px", "fontWeight": "bold", "color": "#333"}),
                                    ],
                                    style={
                                        "backgroundColor": "#f8f9fa",
                                        "border": "1px solid #dee2e6",
                                        "padding": "10px",
                                        "borderRadius": "5px",
                                        "boxShadow": "0px 2px 8px rgba(0, 0, 0, 0.1)"
                                    },
                                    className="mb-4"
                                )
                            ]
                        ),
                    ]
                ),
            ],
            className="mb-4"
        )
    else:
        # A, B, Cがない場合のメッセージ
        return dbc.Card(
            [
                dbc.CardHeader(html.H4("コスト算出"),style={"textAlign": "center"}),
                dbc.CardBody(
                    [
                        dbc.Alert(["コスト算出に用いる式が設定されていません。",
                                  html.Br(),
                                  "右上の『編集』ボタンからコスト算出式を設定してください。", 
                        ],color="warning"),
                    ]
                ),
            ],
            className="mb-4"
        )


def catalog_details_layout(test_id):
    # test_id からテストデータを取得
    test_data = catalog_db.get_catalog_by_id(test_id)

    # カタログデータがない場合のデフォルトメッセージ
    if not test_data:
        return html.Div("該当のテストデータが存在しません。")

    # テスト名と詳細、コストデータを取得
    test_name = test_data[1]

    # テストコスト算出に用いる式A, B, C
    a_formula = test_data[11]
    b_formula = test_data[12]
    c_formula = test_data[13]

    # カタログのレイアウトを返す
    return html.Div(
        style={'padding-left': '20px', 'padding-right': '20px', 'padding-top': '20px'},
        children=[
            # タイトル部分
            html.Div(
                style={'text-align': 'center', 'margin-bottom': '20px'},
                children=[
                    html.H1(test_name, style={'margin': '0'})  # 中央にテスト名
                ]
            ),
            
            # 戻るボタンと編集ボタンを配置
            html.Div(
                style={'display': 'flex', 'justify-content': 'space-between'},  # ボタンの配置
                children=[
                    dcc.Link("カタログ一覧へ戻る", href="/catalog", className="btn btn-secondary"),  # カタログ一覧へ戻るボタン
                    dcc.Link("編集", href=f"/catalog/edit/{test_id}", className="btn btn-warning")  # 編集ボタン
                ]
            ),

            # 詳細要素とコスト算出要素を配置
            html.Div(
                style={'display': 'flex', 'flex-direction': 'column', 'margin-top': '30px'},
                children=[
                    # 詳細セクション
                    html.Div(
                        style={'margin-bottom': '30px'},
                        children=[
                            html.Div([
                                html.P('テスト概要', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[2],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('品質特性との関連', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[3],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                    })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('テスト目的', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[4],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                    })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('テスト対象', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[5],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                    })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('実行手順', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[7],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                    })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('測定値の計算方法', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                *[html.P(part, style={'padding': '10px', 'fontSize': 16, 'color': '#555'}) for part in split_text(test_data[8])]
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                            html.Div([
                                html.P('テスト結果', 
                                    style={
                                        'display': 'inline-block',
                                        'text-align': 'left',
                                        'border': '2px solid #007BFF',
                                        'border-radius': '5px',
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'background-color': '#f8f9fa'
                                    }),
                                html.P(test_data[9],
                                    style={
                                        'padding': '10px',
                                        'fontSize': 16,
                                        'color': '#555'
                                    })
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'})
                        ]
                    ),
                    
                    # コスト算出セクション
                    html.Div(
                        children=[
                            generate_cost_section(a_formula, b_formula, c_formula)
                        ]
                    )
                ]
            )
        ]
    )