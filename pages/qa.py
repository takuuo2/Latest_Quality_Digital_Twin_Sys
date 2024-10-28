
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, ALL
import sqlite3
import re
import json
from .core import catalog_db, write_db


# カタログにパラメータを埋め込む
def replace_params(texts, replacements):
    def replace_with_style(match):
            key = match.group(1)
            value = replacements.get(key, match.group(0))
            return f'<span style="color: red;">{value}</span>'  # 色を赤にする例

    replaced_texts = []
    for item in texts:
        if not isinstance(item, str):
            item = str(item)
        replaced_text = re.sub(r'\${([^}]*)}', lambda match: replacements.get(match.group(1), match.group(0)), item)
        replaced_texts.append(replaced_text)
    return replaced_texts

# パラメータ名とその値をJSON形式で取得
def get_params_values(json_str):
    try:
        if isinstance(json_str, str):
            # JSON形式の文字列を辞書オブジェクトに変換
            data = json.loads(json_str)
        else:
            # 辞書オブジェクトの場合、そのまま使用するか、適切な処理を行う
            data = json_str
        catalog_id_index = None
        for i, (key, value) in enumerate(data.items()):
            if key == "catalog_id":
                catalog_id_index = i
                break
        if catalog_id_index is not None:
            result_data = dict(list(data.items())[catalog_id_index + 1:])
            return json.loads(json.dumps(result_data, ensure_ascii=False))
        else:
            return None
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return None

def format_text_for_markdown(text):
    # Markdown 形式の改行マーカーを挿入
    return text.replace('\n', '  \n')



def convert_newlines_to_br(text):
    # 改行文字を <br> タグに変換
    return text.replace('\n', '<br>')

# 目印となる文字列で分割する関数
def split_text(text, delimiter="<br>"):
    return [part.strip() for part in text.split(delimiter)]

""" def create_text_div(text):
    # テキストを改行で分割し、複数の html.P 要素を作成
    paragraphs = split_text(text)
    return html.Div([html.P(p, style={'padding': '10px','fontSize': 16,'color': '#555'}) for p in paragraphs]) """

#全体のレイアウト。呼び出される場所
def qa_layout(params):
    result = catalog_db.get_catalog(params.get("nid", "N/A"))
    content = catalog_db.get_content(params.get("nid", "N/A"))
    print(result[0])

    parameters = get_params_values(content[0][0])
    print(parameters)
    if isinstance(parameters, dict):
        print('Yes')
    else:
        print('No')

    replaced_result = replace_params(result[0], parameters)
    print(replaced_result)

    # テスト結果入力に利用
    values = result[0][10].split(",")
    count = len(values)
    print(values, count)

    nid = params.get("nid", "N/A")
    current_content = write_db.get_current_content(nid)
    test_result = current_content[0].get('test_result')
    print(f' qa 前回データ: {test_result}')
    previous_test_result = ""
    if test_result == None:
        previous_test_result = 'なし'
    else:
        previous_test_result = test_result

    return html.Div([

        ### 品質活動（非機能テスト）の情報
        html.H1(
            replaced_result[1], 
            style={'text-align': 'center', 
                   'padding-top':'20px',
                   'font-family': 'Arial, sans-serif',
                    'color': '#333'
            }
        ),
        html.Div([
            html.P('テスト概要', 
                   style={
                       'display': 'inline-block',
                        'text-align': 'left',
                        'border': '2px solid #007BFF',  # Border color change
                        'border-radius': '5px',  # Rounded corners
                        'padding': '10px',  # Increased padding
                        'fontSize': 16,  # Slightly larger font size
                        'background-color': '#f8f9fa'  # Light background color
                    }
            ),
            html.P(replaced_result[2],
               style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }    
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('品質特性との関連', 
                   style={'display': 'inline-block',
                    'text-align': 'left',
                    'border': '2px solid #007BFF',
                    'border-radius': '5px',
                    'padding': '10px',
                    'fontSize': 16,
                    'background-color': '#f8f9fa'
                    }
                ),
            html.P(replaced_result[3],
                style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('テスト目的', 
                   style={'display': 'inline-block',
                        'text-align': 'left',
                        'border': '2px solid #007BFF',
                        'border-radius': '5px',
                        'padding': '10px',
                        'fontSize': 16,
                        'background-color': '#f8f9fa'
                    }
                ),
            html.P(replaced_result[4],
                style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('テスト対象', 
                   style={'display': 'inline-block',
                    'text-align': 'left',
                    'border': '2px solid #007BFF',
                    'border-radius': '5px',
                    'padding': '10px',
                    'fontSize': 16,
                    'background-color': '#f8f9fa'
                }
            ),
            html.P(replaced_result[5],
                style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('実行手順', 
                   style={'display': 'inline-block',
                        'text-align': 'left',
                        'border': '2px solid #007BFF',
                        'border-radius': '5px',
                        'padding': '10px',
                        'fontSize': 16,
                        'background-color': '#f8f9fa'
                    }
            ),
            html.P(replaced_result[7],
                style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('測定値の計算方法', 
                style={'display': 'inline-block',
                        'text-align': 'left',
                        'border': '2px solid #007BFF',
                        'border-radius': '5px',
                        'padding': '10px',
                        'fontSize': 16,
                        'background-color': '#f8f9fa'
                }
            ),
            *[html.P(part, style={'padding': '10px', 'fontSize': 16, 'color': '#555'}) for part in split_text(replaced_result[8])]
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        html.Div([
            html.P('テスト結果', 
                   style={'display': 'inline-block',
                        'text-align': 'left',
                        'border': '2px solid #007BFF',
                        'border-radius': '5px',
                        'padding': '10px',
                        'fontSize': 16,
                        'background-color': '#f8f9fa'
                    }
            ),
            html.P(replaced_result[9],
                style={
                    'padding': '10px',
                    'fontSize': 16,
                    'color': '#555'
                }
            )
        ], style={'margin': '10px 20px', 'border': '1px solid #ddd', 'border-radius': '5px', 'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Hr(style={'margin': '20px 0'}),

        ### テスト結果入力欄
        dbc.Row(
                [
                    dbc.Col(
                        html.P(
                            'テスト結果:',
                            style={
                                'fontSize': 16,
                                'color': '#333',
                                'font-weight': 'bold'
                            }
                        ),
                        width=2,
                        className='text-center',
                        align='center'
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type': 'input','index': replaced_result[1]},
                            type='number',
                            step='0.01',
                            placeholder=replaced_result[9],
                            className='mb-3',
                            style={'width': '80%', 'border-radius': '5px', 'border': '1px solid #007BFF'}
                        ),
                        width=10
                    )
                ],
                className='mb-3',
                align='center'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Button(
                            '登録',
                            id='register-btn',
                            style={
                                'background-color': '#007BFF',  # Button color
                                'color': 'white',
                                'border': 'none',
                                'padding': '10px 20px',
                                'border-radius': '5px',
                                'fontSize': 16
                            }
                        )
                    ],
                  width='auto'
                )
            ],
            justify='end',
            style={'padding-right': '30px'}
        ),
        dcc.ConfirmDialog(
            id='confirm-dialog',
            message='入力されたデータを登録しますか？'
        ),  

        html.Hr(style={'margin': '20px 0'}),
        html.Div([
            # Header section for the test result title
            html.Div([
                html.P('前回のテスト結果', 
                    style={
                        'display': 'inline-block',
                        'text-align': 'left',
                        'border': '1px solid #B0C4DE',  # Softer, lighter border
                        'border-radius': '6px',  # Softer corners
                        'padding': '8px',  # Moderate padding
                        'fontSize': 16,  # Slightly smaller font size for a subtler look
                        'background-color': '#f5f5f5',  # Light gray background for subtle contrast
                        'color': '#333',  # Darker, less intense text color
                        'font-weight': 'normal'  # Normal weight for a more understated look
                    }
                )
            ], style={'margin-bottom': '8px'}),  # Slightly smaller space between title and content
            
            # Section for the test result content
            html.Div([
                html.P(previous_test_result,
                    style={
                        'padding': '8px',  # Reduced padding for a clean, compact layout
                        'fontSize': 14,  # Slightly smaller font size for a more understated appearance
                        'color': '#444',  # Softer text color for easy reading
                        'background-color': '#fafafa',  # Very light background to create a subtle contrast
                        'border-radius': '6px',  # Matching border radius for consistency
                        'border': '1px solid #ddd',  # Light border for definition
                        'box-shadow': '0 1px 3px rgba(0,0,0,0.08)'  # Soft, minimal shadow for subtle depth
                    }
                )
            ])
        ], style={
            'margin': '8px 16px',  # Slightly smaller margin for a more compact layout
            'padding': '12px',  # Moderately sized padding for a cleaner look
            'border': '1px solid #ddd',  # Soft, light border for subtle separation
            'border-radius': '6px',  # Consistent corner rounding for a smooth, cohesive design
            'box-shadow': '0 2px 4px rgba(0,0,0,0.06)'  # Very light shadow for subtle depth without being too prominent
        }),

        html.Hr(style={'margin': '20px 0'}),
        html.Div(id='register-result', style={"marginTop": "20px"}),
        dcc.Store(id='register-history', data=[]),

        html.Hr(style={'margin': '20px 0'}),
        html.Hr(style={'margin': '20px 0'}),
        html.Hr(style={'margin': '20px 0'}),
        html.Hr(style={'margin': '20px 0'}),
        html.Hr(style={'margin': '20px 0'}),
        # create_categoryを模倣する
    ])

def add_test_result(current_content, test_result):
    # 元の辞書に新しいデータを追加して結合
    current_content['test_result'] = test_result
    return current_content

@callback(
    Output('confirm-dialog', 'displayed'),
    Input('register-btn', 'n_clicks'),
    prevent_initial_call=True
)
def display_confirm_dialog(n_clicks):
    print(f"register-btn clicked: n_clicks={n_clicks}")
    if n_clicks and n_clicks > 0:
        return True  # ボタンが押されたら確認ダイアログを表示
    return False

@callback(
  Output('register-result', 'children'),
  Output('register-history', 'data'),
  Input('confirm-dialog', 'submit_n_clicks'),
  State({'type': 'input', 'index': ALL}, 'value'),
  State('register-history', 'data'),
  State('url', 'href'),
)
def register_data(submit_n_clicks, input_value, history, url):
    print(f"submit_n_clicks: {submit_n_clicks}, input_value: {input_value}")
    if submit_n_clicks:
        if not any(input_value):
            return  "エラー: 入力が必要です。", history, ""
        # データベース登録処理（ここでは仮のデータ処理）
        nid_match = re.search(r'nid=(\d+)', url)
        if nid_match:
            nid = nid_match.group(1)
        current_content = write_db.get_current_content(nid)

        test_result = input_value[0]
        new_content = add_test_result(current_content[0], test_result)
        print(f'new_content : {new_content}')

        # ノードのcontentにテスト結果を登録
        write_db.add_test_result(nid, new_content)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"{timestamp}: 登録完了: {input_value[0]}"
        history.append(new_entry)

        # 履歴と登録結果の表示
        result_display = html.Div([html.P(entry) for entry in history])
        
        return result_display, history
    return "", history

