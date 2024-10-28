import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State,ALL
import sqlite3
from .core import write_db


#カテゴリのプルダウンをQC_DB.dbからフェッチしドロップダウンの作成
def dropdown_category():
  con = sqlite3.connect('./QC_DB.db')
  cursor = con.cursor()
  cursor.execute('SELECT id, category_name FROM categories')
  data = cursor.fetchall()
  cursor.close()
  con.close()
  category_dropdown = []
  category_dropdown = [{'label': str(row[1]), 'value': str(row[0])} for row in data]
  return category_dropdown


'''
●機能：
 ・project_nameとcategory_numを受け取りトップページの画面のレイアウトを返す
●id
 ・input_project_name = ユーザが入力するプロジェクト名
 ・select_category = ユーザが選択するカテゴリ
 ・sprint_now = 現在のするスプリント状態を表示するエリア
 ・sprint_submit = 更新するスプリント状態を表示するエリア
 ・edit_button =  Sprint Planningのボタン
 ・dashboard_button = dashboardのボタン
 ・db_button = QDT-DBのボタン
 ・create_category_button = Create Categoryのボタン
'''
def home_layout(project_name=None, category_num=None):
  return html.Div(
    [
      dbc.Row(
        [
          # プロジェクト情報
          dbc.Col(
            [
              html.H1('<Project Information>'),
              dbc.Row(
                [
                  dbc.Col(
                    html.P('project name:'),
                    width=2,
                    className='text-center',
                    align='center'
                    ),
                  dbc.Col(
                    dbc.Input(
                      id='input_project_name',
                      type='text',
                      placeholder='write project name...',
                      value=project_name,
                      className='mb-3',
                      style={'width': '80%'}
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
                    html.P('Category:'),
                    width=2,
                    className='text-center',
                    align='center'
                    ),
                  dbc.Col(
                    dcc.Dropdown(
                      id='select_category',
                      options=dropdown_category(),
                      multi=False,
                      value=category_num,
                      disabled=False,
                      style={'width': '85%'}
                      ),
                    width=10
                    )
                  ]
                )
              ]
            ),
          # スプリント情報
          dbc.Col(
            [
              html.H1('<Sprint Information>'),
              dbc.Row(
                className='mb-3',
                align='center',
                id='sprint_now'
                ),
              dbc.Row(
                className='mb-3',
                align='center',
                id='sprint_submit'
                )
              ]
            )
          ]
        ),
      html.Hr(),
      #各種ボタン
      dbc.Row(
        [
          html.H1('<Menu>'),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('Sprint Planning', style={'font-size': '30px'}),
                      html.Span('🖊', style={'font-size': '30px'})
                      ],
                    color='secondary',
                    id={'type': 'button', 'index':'edit'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center'
                ),
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('Dashboard',style={'font-size': '30px'}),
                      html.Span('📉',style={'font-size': '30px'})
                      ],
                    color='secondary',
                    id={'type': 'button', 'index':'dashboard'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center',
                ),
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('QDT-DB',style={'font-size': '30px'}),
                      html.Span('💾',style={'font-size': '30px'})
                        ],
                    color='secondary',
                    id={'type': 'button', 'index':'db'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center'
                ),
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('Create Category',style={'font-size': '30px'}),
                      html.Span('🖥️',style={'font-size': '30px'})
                      ],
                    color='secondary',
                    id={'type': 'button', 'index':'category'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center'
                ),
              
              ]
            ),
            html.Hr(),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('NFT', style={'font-size': '30px'}),
                      html.Span('📃', style={'font-size': '30px'})
                      ],
                    color='secondary',
                    id={'type': 'button', 'index':'nft'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center'
              ),
              dbc.Col(
                [
                  dbc.Button(
                    [
                      html.Span('カタログ一覧',style={'font-size': '30px'}),
                      html.Span('📄',style={'font-size': '30px'})
                      ],
                    color='secondary',
                    id={'type': 'button', 'index':'catalog'},
                    style={'width': '80%', 'height': '80px'}
                    )
                  ],
                width=3,
                className='text-center',
                align='center'
              )
            ]
          )
          ]
        )
      ]
    )


'''
●機能：
 ・プロジェクト名とカテゴリから<Sprint Information>の表示を行う
 ・今のスプリントの状態と更新するスプリントの状態を表示するエリアを作成している
●id
 ・sprint_view = 今のスプリントの回数を表示
 ・state_view = 今のスプリントの状態を表示
 ・sprint = 更新するスプリントの回数を入力
 ・state = 更新するスプリントの状態を入力
 ・submit = updateボタン
'''
@callback(
  Output('sprint_now', 'children'),
  Output('sprint_submit', 'children'),
  Input('select_category', 'value'),
  State('input_project_name', 'value'),
  prevent_initial_call=True
)
def update_sprint(category,pname):
  if category is None or pname is None:
    return dash.no_update
  else:
    select = 'SELECT pid, nsprint, status FROM project WHERE pname = %s'
    project = write_db.check_db(select,pname)
    if project == 'none':
      sprint = '-'
      state = '-'
      sprint_value = 1
      state_value = 'planning'
    else:
      sprint = project[1]
      state = project[2]
      sprint_value = project[1]
      state_value = project[2]
    now_children = [
      dbc.Col(
        html.P('current state⇒'),
        width=2,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        html.P('number of sprints:'),
        width=2,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        html.P(sprint, id='sprint_view'),
        width=1,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        html.P('state:'),
        width=1,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        html.P(state, id='state_view'),
        width=2,
        className='text-center',
        align='center'
        )
      ]
    submit_children = [
      dbc.Col(
        html.P('change state⇒'),
        width=2,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        html.P('number of sprints:'),
        width=2,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        dcc.Input(
          id='sprint',
          type='number',
          placeholder=sprint_value,
          style={'width': '85%'}
          ),
        width=1
        ),
      dbc.Col(
        html.P('state:'),
        width=1,
        className='text-center',
        align='center'
        ),
      dbc.Col(
        dcc.Dropdown(
          ['planning', 'doing', 'reviewing'],
          placeholder=state_value,
          id='state'
          ),
        width=2
        ),
      dbc.Col(
        html.Button('update', id='submit', n_clicks=0),
        width=1
        )
      ]
    return now_children, submit_children
  


#スプリントの状態を変更する
@callback(
  Output('sprint_view', 'children'),
  Output('state_view', 'children'),
  Input('submit', 'n_clicks'),
  State('state', 'value'),
  State('sprint', 'value'),
  State('input_project_name', 'value'),
  prevent_initial_call=True
)
def updata(n_click, state, sprint, pname):
    if n_click == 0:
        return dash.no_update, dash.no_update
    else:
        if (state is not None) and (sprint is not None):
          write_db.write_project(pname, sprint, state)
          return sprint, state
        else:
          return '入力エラー', '入力エラー'


#urlを変更する
'''
1. button_listからNoneでない値だけを抽出
2. 押されたボタンのIDを取得
3. project_nameとcategoryが指定されている場合、データベースからプロジェクト情報を取得
4. 取得したプロジェクト情報に基づいて、特定のボタンがクリックされた場合のリダイレクトURLを生成
5. project_nameとcategoryが指定されていない場合、新しいカテゴリを作成するリダイレクトURLを返す
'''
@callback(
  Output('url', 'href'),
  Input({'type': 'button', 'index': ALL}, 'n_clicks'),
  State('input_project_name', 'value'),
  State('select_category', 'value'),
  prevent_initial_call=True
)
def redirect_edit_url(button_list, project_name, category):
  button_check = [value for value in button_list if value is not None]
  if button_check == []:
    return dash.no_update
  ctx = dash.callback_context
  triggered_id = ctx.triggered_id
  button_id = triggered_id['index']
  if project_name != None and category != None:
    select = 'SELECT pid, nsprint, status FROM project WHERE pname = %s'
    project = write_db.check_db(select,project_name)
    sprint_num = str(project[1])
    state = str(project[2])
    pid = str(project[0])
    if project == 'none':
      return dash.no_update
    else:
      if int(project[1])>=1:
        if button_id == 'edit':
          return '/edit?project_name=' + project_name + '&category=' + category + '&sprint_num=' + sprint_num  + '&state=' + state + '&pid=' + pid
        elif button_id == 'db':
          return '/db?&pid=' + pid 
        elif button_id == 'dashboard':
          return '/dashboard?&pid=' + pid + '&sprint_num=' + sprint_num + '&category=' + category
        

  else:
    if button_id =='category':
      return '/create_category'
    elif button_id == 'nft':
      return '/nft'
    elif button_id == 'catalog':
      return '/catalog'
    return dash.no_update