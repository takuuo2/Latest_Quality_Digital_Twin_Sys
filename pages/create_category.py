import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output,State,ALL
import sqlite3



#カテゴリ名を確認する
def check_category(category_name):
    conn = sqlite3.connect('./QC_DB.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories WHERE category_name = ?',(category_name,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
  

#重要度プルダウンの選択肢を作成
def opinion():
  opinion=[
    {'label': '重要度：高','value': 'H'},
    {'label': '重要度：中','value': 'M'},
    {'label': '重要度：低','value': 'L'},
    {'label': '重要度：不要','value': 'N'},
    ]
  return opinion


'''
●機能：
 ・カテゴリ名の作成画面のレイアウト
●id
 ・category_name = ユーザが入力するカテゴリ名
 ・check_category = カテゴリ名を確認&書き込みをする
 ・message = 文字を表示する
'''
up = html.Div(
  [
    dbc.Row(
      [
        html.H1('<category name>'),        
        dbc.Input(id='category_name',
                  type='text',
                  placeholder='input category name...',
                  valid=False,
                  className='mb-3',
                  style={'width': '50%','display': 'inline-block', 'marginleft': '10px'}
                  ),
        dbc.Button('check/save',
                   id='check_category',
                   style={'display': 'inline-block','width':'100px','height': '40px'}
                   ),
        html.Div(id='message')
        ]
      )
    ]
  )


'''
●機能：
 ・各ジャンルの重要度を入力する画面のレイアウト
●id
 ・message1 = 文字を出す
 ・type:buttonでそれぞれのidを作成 
 ・check_detail = 登録ボタン
'''
down = dbc.Row(
  [
    html.H1('<detail>'),
    html.Div(id='message1'),
    dbc.Row(
      [
        dbc.Col(width=1),
        dbc.Col(
          [
            dbc.Row(['機能適合性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':120}),
            dbc.Row(['信頼性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':160}),
            dbc.Row(['機能効率性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':80}),
            dbc.Row(['使用性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':240}),
            ],
          width=1
          ),
        dbc.Col(
          [
            dbc.Row([dbc.Label('機能完全性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('機能正確性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('機能適切性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('成熟性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('可用性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('障害許容性（耐故障性）')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('回復性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('時間効率性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('資源効率性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),  
            dbc.Row([dbc.Label('適切度認識性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('習得性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('運用操作性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('ユーザエラー防止性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('ユーザインタフェース快美性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            dbc.Row([dbc.Label('アクセシビリティ')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}), 
            ],
          width=2
          ),
        dbc.Col(
          [
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'機能完全性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'機能正確性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'機能適切性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}), 
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'成熟性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'可用性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'障害許容性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}), 
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'回復性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'時間効率性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'資源効率性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'適切度認識性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}), 
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'習得性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'運用操作性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'ユーザエラー防止性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'ユーザインタフェース快美性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'アクセシビリティ'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40})
            ],
          width=1
          ),
        dbc.Col(width=1),
        dbc.Col(
          [
            dbc.Row(['セキュリティ'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':200}),
            dbc.Row(['互換性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':80}),
            dbc.Row(['保守性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':200}),
            dbc.Row(['移植性'],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':120})
            ],
          width=1
          ),
        dbc.Col(
          [
            dbc.Row([dbc.Label('機密性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('インテグリティ')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('否認防止性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('責任追及性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('真正性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),  
            dbc.Row([dbc.Label('共存性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('相互運用性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('モジュール性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('再利用性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('解析性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('修正性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('試験性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('適応性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('設置性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            dbc.Row([dbc.Label('置換性')],style={'border': '1px solid black','display': 'flex','text-align': 'center','align-items': 'center','justify-content': 'center','height':40}),
            ],
          width=2
          ),
        dbc.Col(
          [
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'機密性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'インテグリティ'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'否認防止性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}), 
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'責任追及性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}), 
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'真正性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'共存性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'相互運用性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'モジュール性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'再利用性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'解析性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'修正性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'試験性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'適応性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'設置性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Row([dcc.Dropdown(id={'type': 'button', 'index':'置換性'},options=opinion(),value=None)],style={'border': '1px solid black','text-align': 'center','height':40}),
            dbc.Button('commit',id='check_detail',style={'width':'100px','height': '40px'})
            ],
          width=1
          )
        ]
      )
    ]    
  )


#全体のレイアウト。呼び出される場所
def create_category_layout():
  return html.Div(
    [
      up,
      html.Hr(),
      down
      ]
    )
  

#カテゴリ名をDBに書き込む．同じのがあった場合は，書き込みを行わない
@callback(
  Output('message','children'),
  Input('check_category','n_clicks'),
  State('category_name','value'),
  prevent_initial_call=True
  )
def up_data(n_click,input):
  print(input)
  if n_click is None :
    return dash.no_update
  else:
    if input is None:
      return 'カテゴリを入力してください'
    else:
      if check_category(input)==[]:
        conn = sqlite3.connect('QC_DB.db') 
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (category_name) VALUES (?)', (input,))
        conn.commit()
        cursor.close()
        conn.close()
        return 'カテゴリ名を書き込みました.下を記入してください'
      else:
        return '同じ名前のカテゴリが存在します'


#各項目をDBに書き込む
@callback(
  Output('message1','children'),
  Input('check_detail','n_clicks'),
  State({'type': 'button', 'index': ALL}, 'value'),
  State({'type': 'button', 'index': ALL}, 'id'),
  State('category_name','value'),
  prevent_initial_call=True
  )
def input(n_click,value,id,category_name):
  if n_click is None:
    return dash.no_update
  else:
    if None in value:
      return 'すべて入力してください'
    else:
      SQuaRE_list=['機能適合性','機能適合性','機能適合性','信頼性','信頼性','信頼性','信頼性','性能効率性','性能効率性','使用性','使用性','使用性','使用性','使用性','使用性',
                   'セキュリティ','セキュリティ','セキュリティ','セキュリティ','セキュリティ','互換性','互換性','保守性','保守性','保守性','保守性','保守性','移植性','移植性','移植性']
      button_indices = [button['index'] for button in id if button.get('type') == 'button']
      conn = sqlite3.connect('./QC_DB.db')
      cursor = conn.cursor()
      cursor.execute('SELECT id FROM categories WHERE category_name = ?',(category_name,))
      data = cursor.fetchall()
      category_id=data[0]
      for SQuaRE,name,num in zip(SQuaRE_list,button_indices,value):
        cursor.execute('INSERT INTO subcategories (category_id, second_name, third_name, importance) VALUES (?, ?, ?, ?)', (category_id[0], SQuaRE,name,num))
      conn.commit()
      cursor.close()
      conn.close()
      return '書き込み終わりました'