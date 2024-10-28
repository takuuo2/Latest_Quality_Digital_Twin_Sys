import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, ALL
from .core import catalog_db, write_db

# def generate_cost_section(a_formula, b_formula, c_formula):
#     # コスト算出セクションの生成
#     return dbc.Card(
#         [
#             dbc.CardHeader(html.H4("コスト算出"), style={"textAlign": "center"}),
#             dbc.CardBody(
#                 [
#                     html.Div(
#                         [
#                             html.H5("A: 準備コスト", className="text-primary"),
#                             dcc.Input(
#                                 id='a_formula_input',
#                                 value=a_formula,
#                                 type='text',
#                                 style={'width': '100%', 'marginBottom': '10px'}
#                             )
#                         ]
#                     ),
#                     html.Div(
#                         [
#                             html.H5("B: 実施コスト", className="text-primary"),
#                             dcc.Input(
#                                 id='b_formula_input',
#                                 value=b_formula,
#                                 type='text',
#                                 style={'width': '100%', 'marginBottom': '10px'}
#                             )
#                         ]
#                     ),
#                     html.Div(
#                         [
#                             html.H5("C: 分析コスト", className="text-primary"),
#                             dcc.Input(
#                                 id='c_formula_input',
#                                 value=c_formula,
#                                 type='text',
#                                 style={'width': '100%', 'marginBottom': '10px'}
#                             )
#                         ]
#                     ),
#                 ]
#             )
#         ],
#         className="mb-4"
#     )

# 遷移先のページコンテンツ
def updated_page_content(summary, quality_characteristic, purpose, target, execution_steps, calculation_method, result, a_formula, b_formula, c_formula):
    return html.Div([
        html.H2("更新された内容"),
        html.P("データが正常に更新されました。"),
        html.H5("入力された内容:"),
        html.P(f"概要: {summary}"),
        html.P(f"品質特性: {quality_characteristic}"),
        html.P(f"目的: {purpose}"),
        html.P(f"対象: {target}"),
        html.P(f"実施手順: {execution_steps}"),
        html.P(f"計算方法: {calculation_method}"),
        html.P(f"結果: {result}"),
        html.P(f"Aの式: {a_formula}"),
        html.P(f"Bの式: {b_formula}"),
        html.P(f"Cの式: {c_formula}"),
    ])

def catalog_edit_layout(test_id):
    # test_id からテストデータを取得
    test_data = catalog_db.get_catalog_by_id(test_id)

    # カタログデータがない場合のデフォルトメッセージ
    if not test_data:
        return html.Div("該当のテストデータが存在しません。")

    # テスト名を取得
    test_name = test_data[1]

    # テストコスト算出に用いる式A, B, C
    a_formula = test_data[11]
    b_formula = test_data[12]
    c_formula = test_data[13]

    # 編集ページのレイアウトを返す
    return html.Div(
        style={'padding-left': '20px', 'padding-right': '20px', 'padding-top': '20px'},
        children=[
            # タイトル部分
            html.Div(
                style={'text-align': 'center', 'margin-bottom': '20px'},
                children=[
                    html.H2(f"{test_name} カタログを編集・更新する", style={'margin': '0'})  # 中央にテスト名
                ]
            ),
            
            # 戻るボタンと保存ボタンを配置
            html.Div(
                style={'display': 'flex', 'justify-content': 'space-between'},  # ボタンの配置
                children=[
                    dcc.Link("戻る", href=f"/catalog/details/{test_id}", className="btn btn-secondary"),  # カタログ一覧へ戻るボタン
                    dbc.Button("保存", id="save_button_top", color="success")  # 保存ボタン
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
                                dcc.Input(
                                    id='test_summary_input',
                                    value=test_data[2],
                                    type='text',
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Input(
                                    id='quality_characteristic_input',
                                    value=test_data[3],
                                    type='text',
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Input(
                                    id='test_purpose_input',
                                    value=test_data[4],
                                    type='text',
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Input(
                                    id='test_target_input',
                                    value=test_data[5],
                                    type='text',
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Textarea(
                                    id='execution_steps_input',
                                    value=test_data[7],
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Textarea(
                                    id='calculation_method_input',
                                    value=test_data[8],
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
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
                                dcc.Input(
                                    id='test_result_input',
                                    value=test_data[9],
                                    type='text',
                                    style={'width': '100%', 'margin': '10px 0'}
                                )
                            ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                        ]
                    ),
                    
                    # コスト算出セクションを追加
                    #generate_cost_section(a_formula, b_formula, c_formula)
                ]
            ),

            dbc.Card(
                [
                    dbc.CardHeader(html.H4("コスト算出"), style={"textAlign": "center"}),
                    dbc.CardBody(
                        [
                            # 説明文の追加
                            html.Div(
                                [
                                    html.P(
                                        "非機能テストにおけるコストは以下の式の和で計算される。",
                                        style={'fontSize': '1.0rem', 'color': '#6c757d'}  # 小さめのフォントと薄い文字色
                                    ),
                                    html.Div(
                                        "準備にかかるコスト(mh) + 実施にかかるコスト(mh) + 分析にかかるコスト(mh)",
                                        style={
                                            'border': '1px solid #ddd',  # 枠線を追加
                                            'padding': '10px',  # 内側の余白を調整
                                            'backgroundColor': '#f8f9fa',  # 背景色を薄く
                                            'borderRadius': '5px',  # 角丸にして柔らかい印象に
                                            'marginBottom': '20px',
                                            'fontSize': '1rem',  # フォントサイズを調整
                                            'color': '#333'  # 文字色をダークグレーに
                                        }
                                    ),
                                ],
                                style={'marginBottom': '20px'}
                            ),

                            html.Hr(style={'borderColor': '#e9ecef'}),
                            
                            # パラメータの表示
                            html.Div(
                                [
                                    html.H5(f"{test_name}に設定されているパラメータ", style={"color": "#333"}),
                                    html.Div(
                                        f"{test_data[10]}",  # test_data[10]をパラメータとして表示
                                        style={
                                            'border': '1px solid #ddd',  # 枠線を追加
                                            'padding': '10px',  # 内側の余白を調整
                                            'backgroundColor': '#ffeeba',  # 明るい黄色の背景色
                                            'borderRadius': '5px',  # 角丸にして柔らかい印象に
                                            'marginBottom': '20px'
                                        }
                                    )
                                ]
                            ),

                            html.Hr(style={'borderColor': '#e9ecef'}),
                            
                            # 説明文の追加
                            html.Div(
                                [
                                    html.P(
                                        "上記パラメータを用いて、コストを算出するための式A, B, Cを設定してください。",
                                        style={'fontSize': '1.2rem', 'color': '#333'}  # フォントサイズを調整して読みやすく
                                    )
                                ],
                                style={'marginBottom': '20px'}
                            ),
                            
                            # A: 準備コストの式
                            html.Div(
                                [
                                    html.H5("A: 準備コスト", className="text-primary"),
                                    dcc.Input(
                                        id='a_formula_input',
                                        value=a_formula,
                                        type='text',
                                        style={'width': '100%', 'marginBottom': '10px'}
                                    )
                                ]
                            ),
                            
                            # B: 実施コストの式
                            html.Div(
                                [
                                    html.H5("B: 実施コスト", className="text-primary"),
                                    dcc.Input(
                                        id='b_formula_input',
                                        value=b_formula,
                                        type='text',
                                        style={'width': '100%', 'marginBottom': '10px'}
                                    )
                                ]
                            ),
                            
                            # C: 分析コストの式
                            html.Div(
                                [
                                    html.H5("C: 分析コスト", className="text-primary"),
                                    dcc.Input(
                                        id='c_formula_input',
                                        value=c_formula,
                                        type='text',
                                        style={'width': '100%', 'marginBottom': '10px'}
                                    )
                                ]
                            ),
                        ]
                    )
                ],
                className="mb-4"
            ),

            # 保存ボタンを配置
            html.Div(
                style={'display': 'flex', 'justify-content': 'flex-end'},  # ボタンの配置
                children=[
                    dbc.Button("保存", id="save_button_bottom", color="success")  # 保存ボタン
                ]
            ),
            modal,
        ]
    )


# モーダルのレイアウト
modal = dbc.Modal(
    [
        dbc.ModalHeader("登録完了"),
        dbc.ModalBody(["データが正常に登録されました。", html.Br(), 
                       "これを閉じたあとに詳細ページへ戻り、カタログが更新されていることを確認してください。"
                    ]),
        dbc.ModalFooter(
            dbc.Button("閉じる", id="close", className="ml-auto")
        ),
    ],
    id="modal",
    is_open=False,
)

# 保存ボタンのコールバック
@callback(
    Output('modal', 'is_open'),
    Input('save_button_top', 'n_clicks'),
    Input('save_button_bottom', 'n_clicks'),
    Input('close', 'n_clicks'),
    State('modal', 'is_open'),
    State('test_summary_input', 'value'),
    State('quality_characteristic_input', 'value'),
    State('test_purpose_input', 'value'),
    State('test_target_input', 'value'),
    State('execution_steps_input', 'value'),
    State('calculation_method_input', 'value'),
    State('test_result_input', 'value'),
    State('a_formula_input', 'value'),
    State('b_formula_input', 'value'),
    State('c_formula_input', 'value'),
    State('url', 'pathname')
)
def save_catalog(save_clicks_top, save_clicks_bottom, close_clicks, is_open, summary, quality_characteristic, purpose, target, execution_steps, calculation_method, result, a_formula, b_formula, c_formula, pathname):

    print(f"Summary: {summary}")
    print(f"Quality Characteristic: {quality_characteristic}")
    print(f"Purpose: {purpose}")
    print(f"Target: {target}")
    print(f"Execution Steps: {execution_steps}")
    print(f"Calculation Method: {calculation_method}")
    print(f"Result: {result}")
    print(f"A Formula: {a_formula}")
    print(f"B Formula: {b_formula}")
    print(f"C Formula: {c_formula}")

    print(f"pathname: {pathname}")

    print(f"上部ボタンのクリック: {save_clicks_top}, 下部ボタンのクリック: {save_clicks_bottom}, 閉じるボタンのクリック: {close_clicks}")
    # 閉じるボタンがクリックされた場合
    if close_clicks and is_open:
        print("モーダルを閉じる")  # 閉じるボタンのクリックを確認
        return False  # モーダルを閉じる
    
    # データベースへの保存処理を記述
    
    if save_clicks_top or save_clicks_bottom:
        if save_clicks_top:  # 上部ボタンがクリックされた場合
            print("上部ボタンがクリックされました。")
        if save_clicks_bottom:  # 下部ボタンがクリックされた場合
            print("下部ボタンがクリックされました。")
        
        id = int(pathname.split('/')[-1])
        catalog_db.update_catalog(summary, quality_characteristic, purpose, target, execution_steps, calculation_method, result, a_formula, b_formula, c_formula, id)
        print("データが登録されました。")  # 実際のデータ保存処理をここに追加
        
        return True  # モーダルを開く
    
    
    return is_open  # 何も変わらない場合はそのまま