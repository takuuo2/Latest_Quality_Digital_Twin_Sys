import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State, ALL
from .core import catalog_db, write_db

def catalog_layout(params):
    test_data = catalog_db.get_catalogs()
    
    # カタログのカードを生成
    test_cards = [create_test_card(test) for test in test_data]

    # target_qcのユニークな値を取得し、プルダウンメニューの選択肢を生成
    target_qc_options = [{'label': qc, 'value': qc} for qc in set(test['target_qc'] for test in test_data)]

    return html.Div(
        style={'padding-left': '20px', 'padding-right': '20px', 'padding-top': '20px'},  # 上の余白を追加
        children=[
            html.Div(
                style={'text-align': 'center', 'margin-bottom': '20px'},  # 中央揃えのスタイル
                children=[
                    html.H1("非機能テストカタログ一覧", style={'margin': '0'})  # 中央にタイトル
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justify-content': 'space-between'},  # ボタンの配置
                children=[
                    dcc.Link("ホームへ戻る", href="/home", className="btn btn-secondary"),  # 戻るボタン
                    dcc.Link("カタログ追加", href="/catalog/add", className="btn btn-success")  # カタログ追加ボタン
                ]
            ),
            # プルダウンメニューを追加
            html.Div(
                dcc.Dropdown(
                    id='target-qc-filter',
                    options=[{'label': '全て', 'value': ''}] + target_qc_options,  # 「全て」を含めたオプション
                    value='',  # 初期値は全て表示
                    clearable=False,
                    style={
                        'width': '300px',  # プルダウン自体の幅
                        'margin-top': '20px', 
                        'margin-bottom': '20px'
                    }
                ),
                style={
                    'display': 'flex',           # フレックスボックスレイアウトを使用
                    'justify-content': 'center',  # 水平方向に中央に配置
                    'align-items': 'center',      # 垂直方向にも中央に揃えたい場合（オプション）
                    'width': '100%',              # 親要素の幅を全体にする
                }
            ),
            html.Div(
                id='card-container',  # カードを表示するためのDiv
                children=test_cards,
                style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'}  # カードを中央揃えにする
            )
        ]
    )


def create_test_card(test):
    return dbc.Card(
        dbc.CardBody(
            style={'position': 'relative', 'padding': '20px'},  # カードのパディング
            children=[
                # target_qcを右上に配置
                html.Div(
                    dbc.Card(
                        dbc.CardBody(
                            html.P(
                                test['target_qc'],
                                className="card-text",
                                style={
                                    'margin': '0',
                                    'white-space': 'nowrap',  # 折り返しを防ぐ
                                    'font-size': '1.0em',  # フォントサイズを小さく
                                    'overflow': 'hidden',      # はみ出た部分を隠す
                                    'text-overflow': 'ellipsis' # テキストがはみ出た場合は...と表示
                                }
                            ),
                        ),
                        className="target-qc-card",
                        style={
                            'border': '1px solid #007bff',  # 枠線の色
                            'border-radius': '5px',  # 枠線の角を少し丸める
                            'padding': '3px',  # 枠内のパディングを小さく
                            'margin': '0',  # マージンをなしに
                            'max-width': '150px',  # 枠線の最大幅を設定
                            'height': '30px',  # 高さを設定
                            'display': 'flex',  # 中央に配置するためにflexを使用
                            'align-items': 'center',  # 縦方向に中央に配置
                            'justify-content': 'center',  # 横方向に中央に配置
                        }
                    ),
                    style={
                        'position': 'absolute',
                        'top': '10px', 
                        'right': '10px',
                    }
                ),
                
                # nameをtarget_qcと詳細を見るの中間に配置
                html.H5(test['name'], className="card-title text-center", style={
                    'margin': '50px 0 30px 0',  # 上下のマージンを調整
                    'font-weight': 'bold',
                    'font-size': '1.3em'
                }),

                # 詳細ページへのリンクを中央に配置
                dcc.Link("詳細を見る", href=f"/catalog/details/{test['id']}", className="btn btn-primary mt-2 d-block mx-auto", style={'width': '120px'})  # 横幅を120pxに設定
            ]
        ),
        className="test-card",
        style={
            'border': '1px solid #ccc',
            'border-radius': '10px',
            'margin': '10px',
            'max-width': '480px',  # カードの最大幅を設定
            'width': '100%',  # 横幅を100%に設定
            'position': 'relative',  # target_qcを絶対位置にするための設定
            'background-color': '#f8f9fa',  # カードの背景色
            'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',  # 影を追加
        },
    )


# コールバックを追加
@callback(
    Output('card-container', 'children'),
    Input('target-qc-filter', 'value')
)
def update_cards(selected_target_qc):
    test_data = catalog_db.get_catalogs()
    
    # target_qcでフィルタリング
    if selected_target_qc:
        filtered_data = [test for test in test_data if test['target_qc'] == selected_target_qc]
    else:
        filtered_data = test_data  # 全て表示

    # カードを生成
    return [create_test_card(test) for test in filtered_data]