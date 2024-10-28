from datetime import datetime
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, callback, MATCH
from dash.dependencies import Input, Output, State, ALL
from matplotlib import category
import pandas as pd
import re

from pages.qa import split_text
from .core import write_db, node_calculation, catalog_db
from node import quality_node, quality_activity, quality_implementation, quality_requirement
from task import task
import plotly.graph_objs as go
import sqlite3
from dash.exceptions import PreventUpdate
import json
import psycopg2
from nft import redmine
import uuid
import spacy

nlp = spacy.load('ja_core_news_sm')

#Excelのファイル名とシート名
e_base = '保守性_DB.xlsx'
e_square = 'SQuaRE'
e_maintainability = 'maintainability'
e_architecture = 'architecture'
e_request = 'request'

e_base2 = 'QiU要求+PQ要求.xlsx'
e_qiu = 'QiUR'
e_pq = 'PQR'


#データの読み取り
df_square = pd.read_excel(e_base, sheet_name=[e_square])
df_maintainability = pd.read_excel(e_base, sheet_name=[e_maintainability])
df_architecture = pd.read_excel(e_base, sheet_name=[e_architecture])
df_request = pd.read_excel(e_base, sheet_name=[e_request])

df_qiu = pd.read_excel(e_base2, sheet_name=[e_qiu])
df_pq = pd.read_excel(e_base2, sheet_name=e_pq)
df_pq2 = pd.read_excel(e_base2, sheet_name=[e_pq])


# グラフ作成
def make_data(mae, now):
  labels = ['達成', '未達成']
  previous = [now, 100 - now]
  current = [mae, 100 - mae]
  colors = ['#FF9999', 'rgb(255, 0, 0)']
  trace_previous = go.Pie(
    labels=labels,
    values=previous,
    sort=False,
    hole=0,
    textinfo='none',  
    hoverinfo='none',
    marker=dict(colors=[colors[1], 'rgba(0,0,0,0)'],
                line=dict(color='black', width=1))
    )
  trace_current = go.Pie(
    labels=labels,
    values=current,
    hole=0,
    sort=False,
    textinfo='none',  
    hoverinfo='none',
    marker=dict(colors=[colors[0], 'rgba(0,0,0,0)'],
                line=dict(color='black', width=1))
    )
  figure = go.Figure(data=[trace_previous, trace_current])
  figure.update_layout(
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=9),
    autosize=False,
    height=37,
    width=37,
    margin=dict(l=1, r=1, t=1, b=1),
    )
  return figure


# 貢献度％計算
tree_contribution = []
tree_name = []
def calculate_contribution_percentage(node, x=None):
  global tree_contribution, tree_name
  if node is None:
    return None
  elif type(node) != str:
    if x == None:
      tree_name = []
      tree_contribution = []
    if node.children is not None:
      total_contribution = 0
      child_contribution = []
      child_name = []
      for child in node.children:
        total_contribution += child.contribution
        child_name += [child.id]
        child_contribution += [child.contribution]
      for x, y in zip(child_name, child_contribution):
        tree_name += [x]
        tree_contribution += [round(y/total_contribution*100)]
      for child in node.children:
        calculate_contribution_percentage(child, x=1)
    return 0
  else:
    for x, y in zip(tree_name, tree_contribution):
      if x == node:
        return y


# 貢献度を数字に変換
def chenge_int(x):
  if x == 'H':
    return int(3)
  elif x == 'M':
    return int(2)
  elif x == 'L':
    return int(1)
  else:
    return int(0)

# 文の改行処理
def insert_line_breaks(text):
  delimiters = ['[', '○', '×', '・', '①', '②']
  for delimiter in delimiters:
    text = text.replace(delimiter, '￥￥' + delimiter)
  delimiters = ['￥￥']
  pattern = '|'.join(map(re.escape, delimiters))
  parts = re.split(pattern, text)
  if parts[0] == '':
    parts.pop(0)
  for i in range(len(parts) - 1):
    parts.insert(2 * i + 1, html.Br())
  return parts


# 貢献度を検索
def search(category_num, node):
    conn = sqlite3.connect('QC_DB.db')
    cursor = conn.cursor()
    # テーブルからデータを取得
    cursor.execute(
        'SELECT importance FROM subcategories WHERE category_id = ? AND third_name = ?', (category_num, node))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    re_data = data[0]
    return chenge_int(re_data[0])

# カテゴリのプルダウンの作成
def dropdown_sub(category_num, SQuaRE_name):
  options = []
  if SQuaRE_name == '保守性' or SQuaRE_name == '移植性':
    list = ('H', 'M', 'L', 'N')
    color_list = ('red', 'orange', 'LightGreen', 'MediumTurqoise')
    conn = sqlite3.connect('QC_DB.db')
    cursor = conn.cursor()
    cursor.execute('SELECT third_name, importance FROM subcategories WHERE category_id = ? AND second_name = ?', (category_num,SQuaRE_name,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    x = 0
    for i in list:
      for num in data:
        if num[1] == i:
          options.append({'label': html.Div(num[0], style={'color': color_list[x], 'font-size': 15}),'value': num[0]})
      x = x+1

  return options

# 要求文の選択肢の作成
def make_request(node, node_data):
  options = []
  new_options = []
  current_category = None
  if node in {'モジュール性', '再利用性', '解析性', '修正性', '試験性'}:
    for row in df_request[e_request].values:
      if row[1] == node:
        options += [{'label': row[2],'value': row[2]}]
  elif node in {'有効性', '効率性', '満足性', 'リスク回避性', '利用状況網羅性'}: #利用時品質の場合
    for row in df_qiu[e_qiu].values:
      if row[1] == node:
        options += [{'label': row[2],'value': row[2]}]
  else:
    for _, row in df_pq.iterrows():
      category = row[df_pq.columns[1]]
      value = row[df_pq.columns[2]]
      # 新しいカテゴリが始まる場合
      if category != current_category:
          current_category = category
          options.append({
                  'label': html.Div(current_category, style={'font-size': 15, 'border': '1px solid #000000'}),
                  'value': 0,
                  'disabled': True
              })
      # 現在のカテゴリに対する選択肢を追加
      options.append({
          'label': value,
          'value': value
      })
  seen = set()
  new_options = []
  for option in options:
      option_tuple = (option['label'], option['value'])
      if option_tuple not in seen:
          seen.add(option_tuple)
          new_options.append(option)
  #new_options = [dict(t) for t in {tuple(d.items()) for d in options}]
  if node_data.children is not None:
    for children in node_data.children:
      #保守性の副特性における既に選択されているものを選択できなくする
      for row in df_request[e_request].values:
        if row[3] == children.id or row[7] == children.id:
          for option in new_options:
            label = option['label']
            if label == row[2]:
              option['disabled'] = True
      #利用時品質特性で同様の操作
      for row in df_qiu[e_qiu].values:
        if row[2] == children.id:
          for option in new_options:
            label = option['label']
            if label == row[2]:
              option['disabled'] = True
      #製品品質特性で同様の操作
      for row in df_pq2[e_pq].values:
        if row[2] == children.id:
          for option in new_options:
            label = option['label']
            if label == row[2]:
              option['disabled'] = True
      # 保守性のみの処理
      if children.id == '修正量の低減':
        for row_2 in df_request[e_request].values:
          if row_2[8] == 2:
            for option in new_options:
              label = option['label']
              if label == row_2[2]:
                option['disabled'] = True
          
  return new_options

def extract_keywords(text):
    """
    自然言語処理を使ってキーワードを抽出する関数
    """
    doc = nlp(text)
    
    # 名詞や固有名詞を抽出
    keywords = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:  # 名詞や固有名詞を対象にする
            keywords.append(token.text)
    
    # 重複を排除
    unique_keywords = list(set(keywords))
    
    return unique_keywords


def make_options_from_catalog(node_subchar, node_data):
    print(f'node_data : {node_data.id} ')
    options = []
    results = catalog_db.get_catalog_by_subchar(node_subchar)
    print(f'result : {results}')
    options = [{'label': row[0], 'value': row[0], 'extra_data': row[1]} for row in results]
    print("取得したオプション:", options)  # デバッグ用

    keywords = extract_keywords(node_data.id)
    print("抽出されたキーワード:", keywords)  # デバッグ用

    related_options = []
    # 各オプションに対して関連スコアを計算
    for option in options:
        score = sum(1 for keyword in keywords if keyword in option['extra_data'])  # 一致したキーワードの数をカウント
        if score > 0:  # 一致があれば関連オプションに追加
            related_options.append((score, option))  # スコアとオプションをタプルで追加
            print(f"オプション '{option['label']}' のスコア:", score)  # デバッグ用

    # スコアに基づいて関連オプションをソート（スコアの高い順）
    related_options.sort(reverse=True, key=lambda x: x[0])
    print("スコア順にソート後の関連オプション:", related_options)  # デバッグ用

    new_options = []

    # 一番高いスコアを持つものを取得
    if related_options:
        highest_score = related_options[0][0]
        highest_score_options = [opt for score, opt in related_options if score == highest_score]
        
        print("一番高いスコア:", highest_score)  # デバッグ用
        print("一番高いスコアの選択肢:", highest_score_options)  # デバッグ用

        # new_options.append({'label': '関連性の高い非機能テスト', 'value': '', 'disabled': True, 'style': {'border': '2px solid #ccc', 'padding': '5px'}})
        new_options.append({
                  'label': html.Div('特に関連性の高いテスト', style={'border': '2px solid #228B22', 'padding': '5px', 'margin': '5px 0', 'color':'#000000', 'font-weight': 'bold'}),
                  'value': 0,
                  'disabled': True
              })
        new_options.extend(highest_score_options)
    
        # 次に高いスコアのものを取得（存在する場合のみ）
        next_highest_options = [opt for score, opt in related_options if score < highest_score]
        print("next_highest_options:", next_highest_options)  # デバッグ用
        if next_highest_options:
            next_highest_scores = [score for score, opt in related_options if score < highest_score]
            next_highest_score = next_highest_scores[0] if next_highest_scores else None  # 二番目に高いスコアを取得

            print("二番目に高いスコア:", next_highest_score)  # デバッグ用
            print("二番目に高いスコアの選択肢:", next_highest_options)  # デバッグ用

            if next_highest_score is not None:
                # new_options.append({'label': '関連のありそうな非機能テスト', 'value': '', 'disabled': True, 'style': {'border': '2px solid #ccc', 'padding': '5px'}})
                new_options.append({
                  'label': html.Div('関連性がありそうなテスト', style={'border': '2px solid #FFA500', 'padding': '5px', 'margin': '5px 0', 'color': '#333333'}),
                  'value': 0,
                  'disabled': True
              })
                new_options.extend(next_highest_options)

    # 重複を防ぐためのセットを使用
    seen = set()
    unique_options = []
    for option in new_options:
        option_tuple = (option['label'], option['value'])
        if option_tuple not in seen:
            seen.add(option_tuple)
            unique_options.append(option)

    return unique_options

#########################################################
# 機能：   品質実現/活動の選択肢（option)の作成
# 入力：   PQ要求文
# 戻り値： 選択肢（option）
#########################################################
#各名称の作成
def make_adovaic_node(node):
  options = []
  options += [
        {
          'label': html.Div('<品質実現>', style={'font-size': 15}),
          'value': 0,
          'disabled': True
          }
        ]
  for row in df_request[e_request].values:
    if row[2] == node:
      for ri in df_architecture[e_architecture].values:
        if ri[3] == row[7]:
          options += [
            {
              'label': html.Div(ri[3], style={'font-size': 15}),
              'value': ri[3]
              }
            ]
  options += [
    {
      'label': html.Div('<品質活動>', style={'font-size': 15}),
      'value': 0,
      'disabled': True
      }
    ]
  for row in df_request[e_request].values:
    if row[2] == node:
      options += [
        {
          'label': html.Div(row[3], style={'font-size': 15}),
          'value': row[3]
          }
        ]
  return options


#########################################################
# 機能：   品質実現/活動の選択肢（option)の作成＜子あり＞
# 入力：   PQ要求文
# 戻り値： 選択肢（option）
#########################################################
def make_adovaic_node_children(node, node_data):
  options = []
  for row in df_request[e_request].values:
    if row[3] == node or row[7] == node:
      options += [{'label': html.Div('<品質実現>', style={'font-size': 15}),'value': 0,'disabled': True}]
      for ri in df_architecture[e_architecture].values:
        if ri[3] == row[7]:
          options += [{'label': html.Div(ri[3], style={'font-size': 15}),'value': ri[3]}]
      options += [{'label': html.Div('<品質活動>', style={'font-size': 15}),'value': 0,'disabled': True}]
      options += [{'label': html.Div(row[3], style={'font-size': 15}),'value': row[3]}]
  for option in options:
    value = option['value']
    if value == node:
      option['disabled'] = True
  if node_data.children is not None:
    for option in options:
      value = option['value']
      for children in node_data.children:
        if value == children.id:
          option['disabled'] = True
 
  return options

def make_adovaic_node_children_1(node_data):
  options = []
  new_options = []
  for row in df_request[e_request].values:
    if row[8] == 2:
      options += [{'label': row[2],'value': row[2]}]
  new_options = [dict(t) for t in {tuple(d.items()) for d in options}]
  if node_data.children is not None:
    for children in node_data.children:
      for row in df_request[e_request].values:
        if row[3] == children.id or row[7] == children.id:
          for option in new_options:
            label = option['label']
            if label == row[2]:
              option['disabled'] = True
  return new_options

# 貢献度のプルダウンデータ
def select_data():
  data = [
    {'label': '貢献度：高', 'value': '3'},
    {'label': '貢献度：中', 'value': '2'},
    {'label': '貢献度：低', 'value': '1'},
    {'label': '貢献度：不要', 'value': '0'}
    ]
  return data

#貢献度保存用変数
save_percent = []
def update_save_percent(num, text):
    global save_percent
    
    # 既存のtextがある場合は値を更新
    for item in save_percent:
        if item[1] == text:
            item[0] = num
            return
    
    # 既存のtextがない場合は新しい要素を追加
    save_percent.append([num, text])


#左の作成
def message_display(node,pid):
  if node is None:
    return None
  else:
    children = []
    #品質実現
    for row in df_architecture[e_architecture].values:
      if row[3] == node:
        children = [
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<基本戦略>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=2,
                align='center'),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[1]),id='ar_base')
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<個別戦略>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=2,
                align='center'),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[2]),id='ar_in'),
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<説明>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=2,
                align='center',
                ),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[4]),id='ar_exa')
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<前提条件>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[5]),id='ar_tec'),
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<実現手段一覧>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[6]),id='ar_tec'),
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<実現手段入力>',style={'fontSize': 15, 'fontWeight': 'bold', 'color': 'red'}),
                  ],
                className='text-center',
                width=2,
                align='center',
                ),
              dbc.Col(
                [
                  dbc.Input(id={'type': 'input','index': 're_'+row[3]},
                            type='text',
                            value=write_db.check_description(pid, row[3]),
                            placeholder='手法を記載してください...',
                            )
                  ]
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<貢献度入力>',style={'fontSize': 15, 'fontWeight': 'bold', 'color': 'red'}),
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  dcc.Dropdown(
                    options=select_data(),
                    id={'type': 'dropdown','index': 're_'+row[3]},
                    placeholder='貢献度...',
                    value=write_db.check_contribution(pid, row[3])
                    )
                  ],
                width=8,
                ),
              dbc.Col(
                [
                  html.Button(
                    '更新',
                    id={'type': 'button','index': 're_'+row[3]},
                    style={'background-color': 'red'}
                    )
                  ],
                width=2
                )
              ]
            )
          ]
        return children
    #品質活動 (保守性)
    for row in df_request[e_request].values:
      if row[3] == node:
        children = [
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<説明>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[4]),id='re_exa'),
                  ],
                width=10
                ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<測定機能>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(insert_line_breaks(row[5]),id='re_ex')
                  ],
                width=5
                ),
              dbc.Col(
                [
                  dbc.Label('<測定A>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  dbc.Label('<測定B>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                width=1
                ),
              dbc.Col(                                
                      [
                        html.P('他研究A',id='re_a'),
                        html.P('他研究B',id='re_b')
                        ],
                      width=4
                      ),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(  
                [   
                  dbc.Label('<Xの許容範囲>',style={'fontSize': 15, 'fontWeight': 'bold', 'color': 'red'})
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  dcc.RangeSlider(
                    0.00,
                    1.00,
                    value=write_db.check_scope(pid, row[3]),
                    id={'type': 'input','index': 're_'+row[3]},
                    tooltip={'placement': 'bottom', 'always_visible': True},
                    marks={
                      0: {'label': '0', 'style': {'color': '#77b0b1'}},
                      0.20: {'label': '0.2'},
                      0.40: {'label': '0.4'},
                      0.60: {'label': '0.6'},
                      0.80: {'label': '0.8'},
                      1: {'label': '1', 'style': {'color': '#f50'}}
                      }
                    )
                  ],
                width=8
                ),
              html.Br(),
              html.Hr()
              ]
            ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<貢献度入力>',style={'fontSize': 15, 'fontWeight': 'bold', 'color': 'red'}),
                  ],
                className='text-center',
                width=2,
                align='center'
                ),
              dbc.Col(
                [
                  dcc.Dropdown(
                    options=select_data(),
                    id={'type': 'dropdown','index': 're_'+row[3]},
                    placeholder='貢献度...',
                    value=write_db.check_contribution(pid, row[3])
                    )
                  ],
                width=7
                ),
              dbc.Col(
                [
                  html.Button(
                    '更新',
                    id={'type': 'button','index': 're_'+row[3]},
                    style={'background-color': 'red'}
                    )
                  ],
                width=2
                )
              ]
            )
          ]
        return children
    #品質活動 (保守性以外)
    catalogs = catalog_db.get_names_of_catalogs()
    print(f'--------message_displayの内容です--------')
    for row in catalogs:
      if row[0] == node:
        print(f' row[0] は {row[0]}')
        catalog_info = catalog_db.get_catalog_by_name(row[0])
        print(f' catalog_info は {catalog_info[0]}')
        catalog_section = [
          dbc.Row(
            [
              dbc.Col(
                  [
                      html.H3(catalog_info[1], style={'textAlign': 'center', 'fontSize': 24, 'fontWeight': 'bold'})
                  ],
                  width=12
              )
            ],
            justify='center',
            className='my-3'  # スペーシング調整
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<テスト概要>',style={'fontSize': 15,'fontWeight': 'bold'}),
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[2],id='nft_a'),
                  ],
                width=9
                ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<関連する品質特性>',style={'fontSize': 14,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[3],id='nft_b')
                  ],
                width=9
                ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<テスト目的>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[4],id='nft_c')
                ],
                width=9
              ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<テスト対象>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[5],id='nft_d')
                ],
                width=9
              ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<実施手順>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[7],id='nft_e')
                ],
                width=9
              ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<測定値の計算方法>',style={'fontSize': 14,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  *[html.P(part) for part in split_text(catalog_info[8])]
                ],
                width=9
              ),
              html.Hr()
            ]
          ),
          dbc.Row(
            [
              dbc.Col(
                [
                  dbc.Label('<テスト結果>',style={'fontSize': 15,'fontWeight': 'bold'})
                  ],
                className='text-center',
                width=3,
                align='center'
                ),
              dbc.Col(
                [
                  html.P(catalog_info[9],id='nft_f')
                ],
                width=9
              ),
              html.Hr()
            ]
          ),
        ]
        params_section = [
          dbc.Row(
            [
              dbc.Col(
                [
                  html.H4('パラメータ入力', style={'textAlign': 'center', 'fontSize': 18, 'fontWeight': 'bold'})
                ],
                width=12
              )
            ],
            className='my-3'  # スペーシング調整
          )
        ]
        params = catalog_info[10].split(',')
        print(f'params : {params}')
        for label in params:
          row = dbc.Row(
              [
                  dbc.Col(
                      [
                          dbc.Label(f'<{label}>', style={'fontSize': 15, 'fontWeight': 'bold'})
                      ],
                      className='text-center',
                      width=2,
                      align='center'
                  ),
                  dbc.Col(
                    [
                      dbc.Input(id={'type': 'input','index': 'nft_'+catalog_info[1]},
                                type='text',
                                value='',
                                placeholder='',
                       )
                    ]
                  ),
              ],
              className='my-4'
          )
          params_section.append(row)
        # support_label = dbc.Row(
        #     [
        #       dbc.Col(
        #         [
        #           html.H4('サポートの設定', style={'textAlign': 'center', 'fontSize': 18, 'fontWeight': 'bold'})
        #         ],
        #         width=12
        #       )
        #     ],
        #     className='my-3'  # スペーシング調整
        #   )
        # params_section.append(support_label)
        # support_row = dbc.Row(
        #   [
        #     dbc.Col(
        #         [
        #           dbc.Label('<貢献度入力>',style={'fontSize': 15, 'fontWeight': 'bold'}),
        #           ],
        #         className='text-center',
        #         width=2,
        #         align='center'
        #         ),
        #       dbc.Col(
        #         [
        #           dcc.Dropdown(
        #             options=select_data(),
        #             id={'type': 'dropdown','index': 'nft_'+catalog_info[1]},
        #             placeholder='貢献度...',
        #             value=write_db.check_contribution(pid, catalog_info[1])
        #           )
        #         ],
        #         width=7
        #         ),      
        #   ]
        # )
        # params_section.append(support_row)
        button_row = dbc.Row(
              [
                dbc.Col(
                  [
                    html.Button(
                      '登録/更新',
                      id={'type': 'button','index': 'nft_'+catalog_info[1]},
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
              justify='end'
        )
        params_section.append(button_row)
        params_section.append(html.Hr(style={'margin': '20px 0'}))
        params_section.append(html.Div(style={'height': '300px'}))

        children = [
          dbc.Card(
            dbc.CardBody(catalog_section),
            style={"backgroundColor": "#f8f9fa"}
          ),
          dbc.Card(
            dbc.CardBody(params_section),
            style={"backgroundColor": "#e9ecef"}
          ),
        ]
        return children
  

#品質状態モデル表示の画面
def tree_display(node, category, pid,indent=''):
  print(f'node.id : {node.id}')
  if node is None:
    return None
  else:
    if node.type != 'QRM':

      aim_node = write_db.check_node(pid,node.id)
      if aim_node == 'none':
        print(f'subtype : {node.subtype}')
        if node.subtype.strip() == 'nft':
          aim_node = write_db.check_uuid(pid, node.id)
        else:
          aim_node = write_db.check_statement(pid, node.id)
      before = write_db.check_achievement_old(pid, node.id)
      print('###### tree_displayの始まり ######')
      print(f'--- node.type : {node.type} ---')
      print(f'--- node.subtype : {node.subtype} ---')
      print(f'---- aim_node : {aim_node} ----')
      now = aim_node[6]
      com = '達成:'+str(now)+'%'
    if node.type == 'REQ':
      cleaned_subtype = node.subtype.strip()
      if node.id == '保守性':
        num = calculate_contribution_percentage(node.id)
        update_save_percent(num, node.id)
        tree = html.Details(
          [
            html.Summary(
              [
                html.P('[' + str(calculate_contribution_percentage(node)) + '%' + ']', style={'display': 'none', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('品質要求', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                dbc.Popover(dbc.RadioItems(options=dropdown_sub(category, node.id),
                                           id={'type': 'radio', 'index': node.id}),
                            target={'type': 'button','index': node.id},
                            body=True,
                            trigger='hover'),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}),
                ]
              )
            ],
          open=True
          )
      elif node.id in {'有効性', '効率性', '満足性', 'リスク回避性', '利用状況網羅性'}:
        num = calculate_contribution_percentage(node.id)
        update_save_percent(num, node.id)
        tree = html.Details(
          [
            html.Summary(
              [
                html.P('[' + str(calculate_contribution_percentage(node)) + '%' + ']', style={'display': 'none', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('利用時品質特性', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                dbc.Popover(dbc.RadioItems(options=make_request(node.id, node),
                                           id={'type': 'radio', 'index': node.id},
                                           
                                          ),
                            target={'type': 'button','index': node.id},
                            body=True,
                            trigger='hover'),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}),
                ]
              )
            ],
          open=True
          )
      elif node.id in {'モジュール性', '再利用性', '解析性', '修正性', '試験性'}:
        num = calculate_contribution_percentage(node.id)
        update_save_percent(num, node.id)
        tree = html.Details(
          [
            html.Summary(
              [
                html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('品質要求', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                dbc.Popover(dbc.RadioItems(options=make_request(node.id, node),
                                           id={'type': 'radio', 'index': node.id}),
                            target={'type': 'button','index': node.id},
                            body=True,
                            trigger='hover',
                            ),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                ]
              )
            ],
          open=True,
          style={'margin-left': '15px'}
          )
      else:
        # QiU要求の場合，PQ要求文の選択肢を表示
        if cleaned_subtype == 'qiu':
          print('subtypeは <qiu>です')
          num = calculate_contribution_percentage(node.id)
          update_save_percent(num, node.id)
          tree = html.Details(
            [
              html.Summary(
                [
                  html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('利用時品質要求', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                  dbc.Popover(
                    [
                      dcc.Input(
                        id={'type': 'popover-input', 'index': node.id},
                        placeholder='Search...',
                        debounce=True,
                        style={'margin-bottom': '10px', 'width': '100%'}
                      ),
                      html.Div(
                        dbc.RadioItems(options=make_request(node.id, node),
                                      id={'type': 'radio', 'index': node.id}),
                        id={'type': 'radio-container', 'index': node.id},
                        style={
                            'max-height': '300px',  # スクロールエリアの高さを設定
                            'overflow-y': 'auto',    # 垂直スクロールを有効にする
                            'width': '250px'         # スクロールエリアの幅を設定
                        }
                      ),
                    ],
                    id={'type': 'popover', 'index': node.id},
                    target={'type': 'button','index': node.id},
                    body=True,
                    trigger='hover',
                    placement='right',
                    #style={'width': '500px'}   Popover全体の幅を設定
                  ),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(figure=make_data(before, now),
                                  config={'displayModeBar': False}),
                        style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                  ]
                )
              ],
            open=True,
            style={'margin-left': '15px'}
            )
        # PQ要求の場合，カタログ（非機能テスト）を表示
        else :
          num = calculate_contribution_percentage(node.id)
          update_save_percent(num, node.id)
          tree = html.Details(
            [
              html.Summary(
                [
                  html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('製品品質要求', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                  dbc.Popover(dbc.RadioItems(options=make_options_from_catalog(node.other['subchar'], node),
                                           id={'type': 'radio', 'index': node.id}),
                            target={'type': 'button','index': node.id},
                            body=True,
                            trigger='hover',
                            ),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(figure=make_data(before, now),
                                  config={'displayModeBar': False}),
                        style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                  ]
                )
              ],
            open=True,
            style={'margin-left': '15px'}
          )
    elif node.type == 'IMP':
      ver = 0
      for row in df_request[e_request].values:
        if row[7] == node.id:
          ver = row[8]
          text = row[2]
          break
      if ver == 1 :
        num = calculate_contribution_percentage(node.id)
        update_save_percent(num, text)
        tree = html.Details(
          [
            html.Summary(
              [
                html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('PQ要求文:', style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': 10}),
                html.Button(text, id={'type': 'button', 'index': 'ex'+node.id}, style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                dbc.Popover(dbc.RadioItems(options=make_adovaic_node_children(node.id, node),
                                           id={'type': 'radio','index': node.id}),
                            id='popover',
                          target={'type': 'button','index': 'ex'+node.id},
                          body=True,
                          trigger='hover',
                          ),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                ]
              )
            ],
          open=True,
          style={'margin-left': '15px'}
          )
        tree.children.append(
          html.Details(
            [
              html.Summary(
                [
                  html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('品質実現', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(
                    figure=make_data(before, now),
                    config={'displayModeBar': False}
                    ),
                         style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                         )
                  ]
                ),
              html.P('実現手法：' + str(node.other),style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
              ],
            style={'margin-left': '15px', 'marginBottom': '5px'}
            )
          )
      elif ver == 2:
        tree = html.Details(
          [
            html.Summary(
              [
                html.P('[＋'+row[9]+']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('PQ要求文:', style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': 10}),
                html.Button(text, id={'type': 'button', 'index': 'ex'+node.id}, style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                dbc.Popover(dbc.RadioItems(options=make_adovaic_node_children(node.id, node),
                                           id={'type': 'radio','index': node.id}),
                            id='popover',
                          target={'type': 'button','index': 'ex'+node.id},
                          body=True,
                          trigger='hover',
                          ),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                ]
              )
            ],
          open=True,
          style={'margin-left': '15px'}
          )
        tree.children.append(
          html.Details(
            [
              html.Summary(
                [
                  html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('品質実現', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(
                    figure=make_data(before, now),
                    config={'displayModeBar': False}
                    ),
                         style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                         )
                  ]
                ),
              html.P('実現手法：' + str(node.other),style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
              ],
            style={'margin-left': '15px', 'marginBottom': '5px'}
            )
          )
      else:
        if node.id == '修正量の低減':
          num = calculate_contribution_percentage(node.id)
          update_save_percent(num, node.id)
          tree = html.Details(
            [
              html.Summary(
                [
                  html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={
                    'display': 'inline-block','fontSize': 12, 'marginRight': '10px'}),
                  html.P('【下記要求2つで実現】', style={
                    'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id='修正量の低減', style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                  dbc.Popover(dbc.RadioItems(options=make_adovaic_node_children_1(node),
                                           id={'type': 'radio','index': node.id}),
                            id='popover',
                          target='修正量の低減',
                          body=True,
                          trigger='hover',
                          ),
                  html.P(com, style={
                    'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(
                    figure=make_data(before, now),
                    config={'displayModeBar': False},
                    ),
                         style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                         )
                  ]
                )
              ],
            style={'margin-left': '15px'}
            )
        elif node.id == 'テスト自動化':
          for row_3 in df_request[e_request].values:
            if row_3[8] == 3:
              resul = row_3[9].split(',')
              text= row_3[2]
              break
          arc_subchar =[]
          arc_descriptiom =[]
          arc_achivement =[]
          req_subchar =[]
          req_tolerance =[]
          req_achivement =[]
          message =[]
          before_achivement =[]
          for row_4 in df_request[e_request].values:
            for x in resul:
              if row_4[7] == x:
                message +=[row_4[2]]
                no_arc =write_db.check_node(pid,row_4[7])
                arc_subchar +=[no_arc[5]['subchar']]
                arc_descriptiom +=[no_arc[5]['description']]
                arc_achivement +=[no_arc[6]]
                no_req = write_db.check_node(pid,row_4[3])
                req_subchar +=[no_req[5]['subchar']]
                req_tolerance +=[no_req[5]['tolerance']]
                req_achivement +=[no_req[6]]
                before_achivement +=[write_db.check_achievement_old(pid,row_4[7])]
                before_achivement +=[write_db.check_achievement_old(pid,row_4[3])]
          num = calculate_contribution_percentage(node.id)
          update_save_percent(num, text)
          tree = html.Details(
            [
            html.Summary(
              [
                html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                html.P('PQ要求文:', style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': 10}),
                html.Button(text, id={'type': 'button', 'index': 'ex'+node.id}, style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(figure=make_data(before, now),
                                 config={'displayModeBar': False}),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                ]
              ),
            html.Details(
              [
                html.Summary(
                  [
                    html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                    html.P('品質実現', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                    html.Button(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                    html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                    html.P(dcc.Graph(
                      figure=make_data(before, now),
                      config={'displayModeBar': False}
                      ),
                           style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                    ]
                  ),
                html.Details(
                  [
                    html.Summary(
                      [
                        html.P('[50%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                        html.P('PQ要求文：', style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': 10}),
                        html.Button(message[0], style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                        html.P('達成:'+str(arc_achivement[0])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                        html.P(dcc.Graph(
                          figure=make_data(before_achivement[0], arc_achivement[0]),
                          config={'displayModeBar': False},
                          ),
                              style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                                                  'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                        ]
                      ),
                    html.Details(
                  [
                    html.Summary(
                      [
                        html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                        html.P('品質実現', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                        html.Button(arc_subchar[0], id={'type': 'button', 'index': arc_subchar[0]}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                        html.P('達成:'+str(arc_achivement[0])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                        html.P(dcc.Graph(
                          figure=make_data(before_achivement[0], arc_achivement[0]),
                          config={'displayModeBar': False}
                          ),
                              style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                              )
                        ]
                      ),
                    html.P('実現手法：' + arc_descriptiom[0],style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'}),
                    html.Details(
                      [
                        html.Summary(
                          [
                            html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                            html.P('品質活動', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                            html.Button(req_subchar[0], id={'type': 'button', 'index': req_subchar[0]}, style={
                                                        'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                            html.P('達成:'+str(req_achivement[0])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                            html.P(dcc.Graph(figure=make_data(before_achivement[1],req_achivement[0] ),config={'displayModeBar': False}),
                                    style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                                        'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                            ]
                          ),
                        html.P('許容範囲：' + str(req_tolerance[0]),
                                            style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
                        ],
                      style={'margin-left': '15px'}
                      )
                    ],
                  style={'margin-left': '15px', 'marginBottom': '5px'}
                  )
              ],
            style={'margin-left': '15px', 'marginBottom': '5px'}
            ),
            html.Details(
              [
                html.Summary(
                  [
                  html.P('[50%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('PQ要求文：', style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': 10}),
                  html.Button(message[1], style={'display': 'inline-block', 'marginRight': '1px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline'}),
                  html.P('達成:'+str(arc_achivement[1])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(
                    figure=make_data(before_achivement[2], arc_achivement[1]),
                    config={'displayModeBar': False},
                    ),
                         style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                                            'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                  ]
                ),
                html.Details(
                  [
                    html.Summary(
                      [
                        html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                        html.P('品質実現', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                        html.Button(arc_subchar[1], id={'type': 'button', 'index': arc_subchar[1]}, style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                        html.P('達成:'+str(arc_achivement[1])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                        html.P(dcc.Graph(
                          figure=make_data(before_achivement[2], arc_achivement[1]),
                          config={'displayModeBar': False}
                          ),
                              style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top','margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                              )
                        ]
                      ),
                    html.P('実現手法：' + arc_descriptiom[1],style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'}),
                    html.Details(
                      [
                        html.Summary(
                          [
                            html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                            html.P('品質活動', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                            html.Button(req_subchar[1], id={'type': 'button', 'index': req_subchar[1]}, style={
                                                        'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                            html.P('達成:'+str(req_achivement[1])+'%', style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                            html.P(dcc.Graph(figure=make_data(before_achivement[3],req_achivement[1] ),config={'displayModeBar': False}),
                                    style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                                        'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                            ]
                          ),
                        html.P('許容範囲：' + str(req_tolerance[1]),
                                            style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
                        ],
                      style={'margin-left': '15px'}
                      )
                    ],
                  style={'margin-left': '15px', 'marginBottom': '5px'}
                  )
              ],
            style={'margin-left': '15px', 'marginBottom': '5px'}
            ),
            ],
          style={'margin-left': '15px'}
          )
 
                    ],
          open=True,
          style={'margin-left': '15px'}
          )
            
                
    elif node.type == 'ACT':
      if node.parent.type != 'IMP':
        #保守性における品質活動
        if node.subtype.strip() == 'sa':
          text = ''
          for row in df_request[e_request].values:
            if row[3] == node.id:
              text = row[2]
              break
          num = calculate_contribution_percentage(node.id)
          update_save_percent(num, text)
          tree = html.Details(
            [
              html.Summary(
                [
                  html.P('[' + str(calculate_contribution_percentage(node.id)) + '%' + ']', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('PQ要求文：', style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 10}),
                  html.Button(text, id={'type': 'button', 'index': 'ex'+node.id}, style={
                                              'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'border': 'none', 'textDecoration': 'underline' }),
                  dbc.Popover(dbc.RadioItems(options=make_adovaic_node_children(node.id, node),id={'type': 'radio', 'index': node.id}),
                              id='popover',
                              target={'type': 'button','index': 'ex'+node.id},
                              body=True,
                              trigger='hover'
                              ),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(figure=make_data(before, now),config={'displayModeBar': False}),
                        style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                            'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                        )
                  ]
                )
              ],
            open=True,
            style={'margin-left': '15px'}
            )
          tree.children.append(html.Details(
            [
              html.Summary(
                [
                  html.P('[100%]', style={'display': 'inline-block', 'fontSize': 12, 'marginRight': '10px'}),
                  html.P('品質活動', style={'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                  html.Button(node.id, id={'type': 'button', 'index': node.id}, style={
                                              'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                  html.P(com, style={'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                  html.P(dcc.Graph(figure=make_data(before, now),config={'displayModeBar': False}),
                        style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                            'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'})
                  ]
                ),
              html.P('許容範囲：' + str(node.other),
                                style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
              ],
            style={'margin-left': '15px'}
            )
          )
        # 非機能テスト表示
        else:
          tree= html.Details(
          [
            html.Summary(
              [
                html.P('[100%]', style={
                  'display': 'inline-block', 'fontSize': 12, 'marginRight': '2px', 'marginRight': '10px'}),
                html.P('品質活動', style={
                  'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                html.Button(catalog_db.get_catalog_name_by_json(node.other), id={'type': 'button', 'index': catalog_db.get_catalog_name_by_json(node.other)}, style={
                  'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                html.P(com, style={
                  'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(
                  figure=make_data(before, now),
                  config={'displayModeBar': False}
                  ),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                           'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                       )
                ]
              ),
            html.P('パラメータ詳細：' + str(get_data_after_catalog_id(node.other)),
                   style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'}),
            ],
          style={'margin-left': '15px'}
          )
      else:
        tree= html.Details(
          [
            html.Summary(
              [
                html.P('[100%]', style={
                  'display': 'inline-block', 'fontSize': 12, 'marginRight': '2px', 'marginRight': '10px'}),
                html.P('品質活動', style={
                  'display': 'inline-block', 'marginRight': '10px', 'border': '1px solid #000000', 'fontSize': 10}),
                html.Button(node.id, id={'type': 'button', 'index': node.id}, style={
                  'display': 'inline-block', 'marginRight': '10px', 'fontSize': 13, 'background': 'none', 'fontWeight': 'bold', 'border': 'none'}),
                html.P(com, style={
                  'display': 'inline-block', 'marginRight': '3px', 'fontSize': 11}),
                html.P(dcc.Graph(
                  figure=make_data(before, now),
                  config={'displayModeBar': False}
                  ),
                       style={'display': 'inline-block', 'width': '0%', 'verticalAlign': 'top',
                                           'margin': '0', 'position': 'relative', 'top': '0px', 'textAlign': 'center'}
                       )
                ]
              ),
            html.P('許容範囲：' + str(node.other),
                   style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'}),
            html.P('測定値：' + str(0.40),
                               style={'display': 'block', 'fontSize': 12, 'margin-left': '30px'})
            ],
          style={'margin-left': '30px'}
          )

    elif node.type == 'QRM':
      tree = html.Details(
        [
          html.Summary(
            [
               html.P('PQ要求文：', style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': 10}),
               html.Span(node.id, id={'type': 'button', 'index': node.id}, style={'display': 'inline-block', 'marginRight': '15px', 'textDecoration': 'underline', 'fontSize': 12}),
               dbc.Popover(dbc.RadioItems(options=make_adovaic_node(node.id),
                                          id={'type': 'radio', 'index': node.id}
                                          ),
                           id='popover',
                           target={'type': 'button','index': node.id},
                           body=True,
                           trigger='hover',
                           )
              ]
            )
          ],
        open=True,
        style={'margin-left': '15px'}
        )
    if node.children:
      children = [tree_display(child, category,pid,indent + '　')for child in node.children]
      tree.children.append(html.Div(children))

  return tree



def create_list_from_activities(activities, nodes,current_pid):
    result = []
    global save_percent
    # ノードの辞書を作成して、nidで検索しやすくする
    node_dict = {node.nid: node for node in nodes}
    current_pid = current_pid
    percent_saved = 1
    for activity in activities:
        content = activity.task
        if isinstance(content, dict):
            content = str(content.get('subchar', ''))
        else:
            # contentが辞書でない場合（例えば、floatの場合）を処理
            content = str(content)
        parent_statement = None
        parent_subchar = None
        nid = activity.nid  # アクティビティの nid を取得
        pid = activity.pid
        # 親ノードの情報を取得
        for row in df_request[e_request].values:
          if row[3] == content:
            parent_statement = row[2]
            task_cost = row[10]
            break
        #taskのコスト情報の更新
        for task in tasks:
          if task.nid == nid:
            task.cost = task_cost
        if activity.parents:
            parent_nid = activity.parents[0]
            parent_node = node_dict.get(parent_nid)
            
            if parent_node and isinstance(parent_node.task, dict):
                # parent_statement = parent_node.task.get('statement')
                parent_subchar = parent_node.task.get('subchar')
        # if current_pid == str(pid) and isinstance(content, dict) and 'subchar' in content:
        if current_pid == str(pid):
            contribution = None
            if(parent_statement == '実行時に柔軟性を持たせる'or'複数のクラスで定義できるようにする'):
              contribution = 1
            for percent, text in save_percent:
                if text == parent_statement:
                    contribution = int(percent)
                    break
                if text == '修正量の低減':
                    percent_saved = percent
            for percent, text in save_percent:
                if text == parent_subchar:
                  if contribution != None:
                    contribution = contribution * percent * 0.01
                    contribution = round(contribution, 1)
                    break
            result.append({
                'nid': nid,
                'name': content,
                'cost': task_cost,
                'parent': parent_subchar,
                'statement': parent_statement,
                'contribution': contribution  
            })
            # parentでソート
        result = sorted(result, key=lambda x: (x['parent'] is None, x['parent']))
    # '実行時に柔軟性を持たせる' または '複数のクラスで定義できるようにする' の statement を持つエントリの数を数える
    statement_count = sum(1 for item in result if item['name'] in ['実行時バインディング成功率', 'ポリモフィズム使用率'])
    # result 内の各エントリをチェックして、contribution を設定
    for item in result:
        if item['name'] in ['実行時バインディング成功率', 'ポリモフィズム使用率']:
            if(item['contribution'] != None):
              if statement_count > 1:
                  item['contribution'] = percent_saved * 0.5 * item['contribution']
              else:
                  item['contribution'] = percent_saved * item['contribution']
    return result


# 品質活動からachievementが1ではないノードを取得
non_achieved_activities = quality_activity.QualityActivity.get_non_achieved_activities()

# 全てのノードを取得
all_nodes = quality_node.QualityNode.fetch_all_nodes()

assignments = task.TaskAssignment.fetch_all_assignments()
tasks = task.Task.fetch_all_tasks() 


selected_tasks = []
selected_members = []


# リストをカードに変換する関数
def create_list_items(items, members):
    return [
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        html.Button(
                            html.Div(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                f"{item['contribution']}%",  # 数字に%を付ける
                                                style={
                                                    'width': '50px', 'height': '100%', 'border': '1px solid #000',
                                                    'padding': '10px', 'textAlign': 'center', 'backgroundColor': 'lightgray',
                                                    'color': 'black', 'fontWeight': 'bold', 'fontSize': '12px',
                                                }
                                            ),
                                            width=1
                                        ),
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Div(item['parent'], style={'font-size': '18px', 'font-weight': 'bold'}),
                                                    html.Div(item['statement'], style={'font-size': '14px', 'font-weight': 'normal'})
                                                ],
                                                style={'width': '100%', 'height': '100%', 'border': '1px solid #000', 'padding': '10px', 'text-align': 'center', 'background-color': 'blue', 'color': 'white'}
                                            ),
                                            width=4
                                        ),
                                        dbc.Col(
                                            html.Div(item['name'], style={'width': '100%', 'height': '100%', 'border': '1px solid #000', 'padding': '10px', 'text-align': 'center', 'background-color': 'dodgerblue', 'color': 'white', 'font-weight': 'bold'}),
                                            width=4
                                        ),
                                        dbc.Col(
                                            html.Div(f"{item['cost']} MH", style={'width': '70px', 'height': '70px', 'borderRadius': '50%', 'border': '1px solid #000', 'padding': '10px', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': 'green', 'color': 'white', 'font-weight': 'bold'}),
                                            width=1
                                        )
                                    ],
                                    align='center'
                                ),
                                className="mb-2",
                                style={'width': '100%', 'margin': 'auto'}
                            ),
                            id={'type': 'card', 'nid': item['nid']},
                            style={'border': 'none', 'background': 'none', 'padding': '0', 'width': '100%', 'marginBottom': '10px'}
                        ),
                        width=9  # ボタン部分の幅を設定
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id={'type': 'dropdown', 'nid': item['nid']},  # nid を使用
                            options=[{'label': member['mname'], 'value': member['mname']} for member in members],
                            placeholder="Select member",
                            style={'width': '100%', 'display': 'none'},  # 初期状態は非表示
                        ),
                        width=3,  # ドロップダウン部分の幅を設定
                    )
                ],
                align='center',
                className="mb-2",
                style={'width': '100%', 'margin': 'auto'}
            )
        ) for item in items
    ]




# モーダルウィンドウ内の要素を作成する関数
def create_modal_content(list_ex, members):
    # 新しいメンバー表用の列とデータ
    member_table_columns = [
        {"name": "Name", "id": "mname"},
        {"name": "SprintResource(MH)", "id": "sprint_resource"},
        {"name": "ResourceUsed(MH)", "id": "used_resource"},
        {"name": "残量(MH)", "id": "RemainingResource"}
    ]
    
    member_table_data = [
        {
            "mname": member["mname"],
            "sprint_resource": member["sprint_resource"],
            "used_resource": member["used_resource"],
            "RemainingResource": member['sprint_resource'] - member['used_resource']
        }
        for member in members
    ]
    
    table_columns = [
    {"name": "Name", "id": "mname"},
    {"name": "Tasks", "id": "AssignedTask"}
    ]

    # メンバーの情報に残りのリソースと割り当てタスクの枠（空白）を追加
    table_data = []
    for member in members:
        assigned_tasks = []
        for assignment in assignments:
            if assignment.mid == member["mid"]:
                assigned_task_name = next((task.tname for task in tasks if task.tid == assignment.tid), "")
                if assigned_task_name:
                    assigned_tasks.append(assigned_task_name)
          
        # リストをカンマ区切りの文字列に変換
        assigned_tasks_str = ", ".join(assigned_tasks) if assigned_tasks else ""
        table_data.append({"mname": member["mname"], "AssignedTask": assigned_tasks_str})

    negative_value_style = [
        {
            'if': {
                'filter_query': '{RemainingResource} < 0'  # RemainingResource が負の値の場合
            },
            'color': 'red'  # 文字を赤くする
        }
    ]
    return dbc.Row(
        [   
            dbc.Col(
              dbc.Col(
                dbc.Row([
                  dbc.Col(
                      html.Div(
                          "保守性への貢献度",
                          style={'width': '100%', 'height': '90%', 'border': '1px solid #000', 'padding': '10px', 'text-align': 'center', 'font-weight': 'bold','fontSize':'8px'}
                      ),
                      width=1
                  ),
                  dbc.Col(
                      html.Div(
                          "実現できる品質要求",
                          style={'width': '80%', 'height': '90%', 'border': '1px solid #000', 'margin': '0 0 0 12px','padding': '10px', 'text-align': 'center', 'font-weight': 'bold','fontSize':'13px'}
                      ),
                      width=2
                  ),
                  dbc.Col(
                      html.Div( 
                          "品質活動（タスク）",
                          style={'width': '100%', 'height': '90%', 'border': '1px solid #000', 'padding': '10px', 'text-align': 'center',  'font-weight': 'bold'}
                          ),
                      width=3
                  ),
                  dbc.Col(
                      html.Div( 
                          "コスト",
                          style={'width': '70px', 'height': '70px', 'borderRadius': '50%', 'border': '1px solid #000', 'padding': '10px', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': 'green', 'color': 'white', 'font-weight': 'bold'}
                          ),
                      width=1
                  ),
                  dbc.Col(
                      html.Div(
                          "作業担当",
                          style={'width': '90%', 'height': '90%', 'border': '1px solid #000', 'margin': '0 12px','padding': '10px', 'text-align': 'center', 'font-weight': 'bold'}
                      ),
                      width=3
                  ),
                ]),
              ),
              width=8
            ),
            dbc.Col(
                html.Div(
                    create_list_items(list_ex, members),
                    style={'max-height': '70vh', 'overflow-y': 'auto'}
                ),
                width=7
            ),
            dbc.Col(
                html.Div(
                    [
                        
                        
                        dash_table.DataTable(
                            id='member-table',
                            columns=member_table_columns,
                            data=member_table_data,
                            style_table={'height': '40%', 'overflowY': 'auto','marginBottom': '0px'},
                            style_cell={'textAlign': 'center'},
                            style_header={'fontWeight': 'bold','fontSize':'12px'},
                            style_data_conditional=negative_value_style
                        ),
                        html.Div(id='total-person-cost', style={'border': '1px solid #000', 'padding': '10px', 'marginTop': '5px', 'textAlign': 'center', 'font-weight': 'bold'}),
                        html.Div(id='remaining-person-cost', style={'border': '1px solid #000', 'padding': '10px', 'marginTop': '5px', 'textAlign': 'center', 'font-weight': 'bold'}),
                        dash_table.DataTable(
                            id='task-table',
                            columns=table_columns,
                            data=table_data,
                            style_table={'height': '40%', 'overflowY': 'auto', 'marginTop': '5px','marginBottom': '0px'},
                            style_cell={'textAlign': 'center'},
                            style_header={'fontWeight': 'bold'},
                        )
                    ],
                    style={'max-height': '70vh','overflow-y': 'auto'}
                ),
                width=5
            )
        ]
    )
members_data = quality_node.Member.fetch_all_members()
members = [
    {
        "mid": member.mid,
        "pid": member.pid,
        "sprint_resource": member.sprint_resource,
        "used_resource": member.used_resource,
        "mname": member.mname,
        "redmine_id": member.redmine_id
    }
    for member in members_data
] 
for assignment in assignments:
    for member in members:
        if member["mid"] == assignment.mid:
            # タスクのコストを加算
            calc_task = next((t for t in tasks if t.tid == assignment.tid), None)
            if calc_task:
                member["used_resource"] += calc_task.cost

current_pid = ""
list_ex = []
selected_pid = ""

selected_pq_req = ''
'''
●機能：
・編集画面のレイアウト
●id:
・select = 品質モデルの利用者から見えるモデル（品質特性の選択）
・model_free = 品質状態モデルを表示する（編集）
・right_free = データを表示する（実現，活動の情報）
'''
def edit_layout(params):
  global current_pid
  global selected_pid
  global list_ex
  global members
  current_pid = params.get("pid")
  selected_pid = current_pid
  # 現在のpidと一致するメンバーだけを含める
  members = [
      {
          "mid": member.mid,
          "pid": member.pid,
          "sprint_resource": member.sprint_resource,
          "used_resource": member.used_resource,
          "mname": member.mname,
          "redmine_id": member.redmine_id
      }
      for member in members_data if str(member.pid) == current_pid
  ]  
  # ノードからリストを作成
  list_ex = create_list_from_activities(non_achieved_activities, all_nodes,current_pid)
  return dbc.Container(
   [
      dbc.Row(
        [
          dbc.Col(
            [
              html.Div(
                [
                  dbc.Row(
                    [
                      html.H5('project', style={'flex-direction': 'column', 'backgroundColor': '#2d3748','color': 'white', 'text-align': 'center', 'height': '4vh'}),
                      html.P('project:', style={'display': 'inline-block', 'width': '70px'}),
                      html.P(params.get("project_name", "N/A"), style={'display': 'inline-block', 'width': '200px'}),
                      html.P('sprint:', style={'display': 'inline-block', 'width': '70px'}),
                      html.P(params.get("sprint_num", "N/A"), style={'display': 'inline-block', 'width': '30px'}),
                      html.P(params.get("state", "N/A"), style={'display': 'inline-block', 'width': '100px'}),
                      ]
                    ),
                  dbc.Row(
                    [
                      html.H5('setting', style={'flex-direction': 'column', 'backgroundColor': '#2d3748','color': 'white', 'text-align': 'center', 'height': '4vh'}),
                      ]
                    ),
                  dbc.Row(
                    [
                      dcc.RadioItems(
                        # setting の品質特性選択欄の押下可否は disabled で (福田)
                        options=[
                          {'label': '有効性', 'value': '有効性'},
                          {'label': '効率性', 'value': '効率性'},
                          {'label': '満足性', 'value': '満足性'},
                          {'label': 'リスク回避性', 'value': 'リスク回避性'},
                          {'label': '利用状況網羅性', 'value': '利用状況網羅性'},
                          {'label': '保守性', 'value': '保守性'},
                          {'label': '移植性', 'value': '移植性'},
                          ],
                        id='select',
                        labelStyle={'display': 'flex','align-items': 'center','width': '100%','background-color': 'white','marginRight': '20px'}
                        )     
                      ],
                    style={'margin': '0', 'background-color': 'white'}
                    ),
                  dbc.Row([
                    dbc.Col(
                      [
                          dbc.Button(
                              "スプリント計画",
                              id="open-body-scroll",
                              n_clicks=0,
                              style={'width': '100%'}
                          ),
                          dbc.Modal(
                              [
                                  dbc.ModalHeader(
                                      dbc.ModalTitle("計画画面")
                                  ),
                                  dbc.ModalBody(
                                      create_modal_content(list_ex, members), 
                                      id='modal-body-content'
                                  ),
                                  html.Div(id='total-cost', style={'border': '1px solid #000', 'padding': '10px', 'marginTop': '20px', 'textAlign': 'center', 'font-weight': 'bold'}),
                                  dbc.ModalFooter(
                                    [
                                      dbc.Button(
                                            "キャンセル",
                                            id="close-body-scroll",
                                            className="me-2",
                                            n_clicks=0,
                                        ),
                                        dbc.Button(
                                          "確定",
                                          id="confirm-button",
                                          className="ms-2",
                                          n_clicks=0,                                        
                                        )
                                    ],
                                    className="d-flex justify-content-end"
                                  ),
                              ],
                              id="modal-body-scroll",
                              scrollable=False,
                              is_open=False,
                              size="xl",
                               
                          ),
                      ]
                    )
                  ])
                  ]
                )
              ],
            width=2
            ),
          dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                      html.Div(
                                        dcc.Slider(
                                            id='width-slider',
                                            min=2,
                                            max=10,
                                            step=0.1,
                                            value=7,
                                            marks=None,
                                            tooltip={"always_visible": False},  # ツールチップを常に表示
                                        ),
                                        style={'padding': '0', 'margin': '0', 'height': '20px','width': '100%'}
                                      )
                                    ],
                                    width=12,
                                    style={'padding': '0', 'margin': '0'}
                                )
                            ],
                            style={'margin': '0', 'padding': '0'}
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                dbc.Row(
                                                    [
                                                        html.H5('Quality Status Model', style={'backgroundColor': 'black', 'color': 'white', 'text-align': 'center', 'height': '4vh'}),
                                                    ]
                                                ),
                                                dbc.Row(
                                                    id='model_free',
                                                    style={'overflow': 'scroll', 'overflowX': 'scroll', 'overflowY': 'scroll', 'height': '90vh', 'whiteSpace': 'nowrap', 'overflowWrap': 'normal'}
                                                )
                                            ]
                                        )
                                    ],
                                    id='left-col',
                                    #width=7,
                                    className='bg-light'
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                dbc.Row(
                                                    [
                                                        html.H5('Imp/Act Info', style={'backgroundColor': '#2d3748', 'color': 'white', 'text-align': 'center', 'height': '4vh'}),
                                                    ]
                                                ),
                                                dbc.Row(
                                                    id='right_free',
                                                )
                                            ]
                                        )
                                    ],
                                    id='right-col',
                                    #width=5
                                )
                            ],
                            style={'margin': '0', 'padding': '0'}
                        )
                    ]
                )
            ],
        style={'height': '95vh'}
        )
      ],
    fluid=True
    )

@callback(
    [Output('left-col', 'width'),
     Output('right-col', 'width')],
    [Input('width-slider', 'value')]
)
def update_widths(slider_value):
    left_width = max(int(slider_value), 1) 
    right_width = 12 - left_width
    right_width = max(right_width, 1) 
    return left_width, right_width

### スプリント計画 コールバック ###
# 「スプリント計画」 -> モーダルウィンドウ
@callback(
    [Output("modal-body-scroll", "is_open"),
     Output("modal-body-content", "children")],
    [Input("open-body-scroll", "n_clicks"), 
     Input("close-body-scroll", "n_clicks"),
     Input("confirm-button", "n_clicks")],
    [State("modal-body-scroll", "is_open"),
     State({'type': 'card', 'index': ALL}, 'style')]
)
def toggle_modal(open_clicks, close_clicks, confirm_clicks, is_open, card_styles):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "open-body-scroll":
        global list_ex
        global current_pid
        # 品質活動からachievementが1ではないノードを取得
        non_achieved_activities = quality_activity.QualityActivity.get_non_achieved_activities()
        # 全てのノードを取得
        all_nodes = quality_node.QualityNode.fetch_all_nodes()
        list_ex = create_list_from_activities(non_achieved_activities, all_nodes, current_pid)
        return True, create_modal_content(list_ex, members)
    elif button_id == "close-body-scroll":
        return False, dash.no_update
    elif button_id == "confirm-button":
        # 確認ボタンが押されたときの処理
        update_database()

        global selected_pid
        dispatch_issues(selected_pid, selected_tasks, selected_members)
        return False, dash.no_update
    return is_open, dash.no_update

def update_database():
    connector = write_db.get_connector()

    try:
        with connector.cursor() as cursor:
            # Taskテーブルの更新
            for task_obj in tasks:
                task_query = """
                INSERT INTO task (tid, tname, nid, cost, parameter)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (tid)
                DO UPDATE SET
                    tname = EXCLUDED.tname,
                    nid = EXCLUDED.nid,
                    cost = EXCLUDED.cost,
                    parameter = EXCLUDED.parameter
                """
                parameter_json = json.dumps(task_obj.parameter)  # 辞書をJSON文字列に変換
                cursor.execute(task_query, (task_obj.tid, task_obj.tname, task_obj.nid, task_obj.cost, parameter_json))

            # Memberテーブルの更新
            for member in members:
                member_query = """
                INSERT INTO member (mid, mname, pid, sprint_resource, used_resource, redmine_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (mid)
                DO UPDATE SET
                    mname = EXCLUDED.mname,
                    pid = EXCLUDED.pid,
                    sprint_resource = EXCLUDED.sprint_resource,
                    used_resource = EXCLUDED.used_resource,
                    redmine_id = EXCLUDED.redmine_id
                """
                cursor.execute(member_query, (member['mid'], member['mname'], member['pid'], member['sprint_resource'], member['used_resource'], member['redmine_id']))

            # TaskAssignmentテーブルの更新
            for assignment in assignments:
                # 既存のレコードを削除するクエリ
                delete_query = """
                DELETE FROM task_assignment WHERE tid = %s
                """
                cursor.execute(delete_query, (assignment.tid,))
                
                # 新しいレコードを挿入するクエリ
                insert_query = """
                INSERT INTO task_assignment (tid, mid)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (assignment.tid, assignment.mid))
        # トランザクションをコミット
        connector.commit()

    except Exception as e:
        # エラーが発生した場合はロールバック
        connector.rollback()
        raise e

    finally:
        # コネクションを閉じる
        connector.close()




# タスク割り当て コールバック
@callback(
    [Output({'type': 'card', 'nid': ALL}, 'style'),
     Output('total-cost', 'children'),
     Output({'type': 'dropdown', 'nid': ALL}, 'style'),
     Output('task-table', 'data'), 
     Output('member-table', 'data'),
     Output('total-person-cost', 'children'),
     Output('remaining-person-cost', 'children')],  
    [Input({'type': 'card', 'nid': ALL}, 'n_clicks'),
     Input({'type': 'dropdown', 'nid': ALL}, 'value')],
    [State({'type': 'card', 'nid': ALL}, 'style'),
     State({'type': 'dropdown', 'nid': ALL}, 'style'),
     State({'type': 'dropdown', 'nid': ALL}, 'id')]
)
def update_selection(n_clicks, selected_values, card_styles, dropdown_styles, dropdown_ids):
    if not n_clicks:
        raise PreventUpdate
    total_cost = 0
    new_card_styles = []
    new_dropdown_styles = []

    # リストの長さを合わせる
    num_items = len(n_clicks)
    if len(card_styles) < num_items:
        card_styles.extend([{} for _ in range(num_items - len(card_styles))])
    if len(dropdown_styles) < num_items:
        dropdown_styles.extend([{} for _ in range(num_items - len(dropdown_styles))])

    for i, clicks in enumerate(n_clicks):
        if clicks and clicks % 2 == 1:
            card_styles[i]['backgroundColor'] = '#d3d3d3'
            dropdown_styles[i]['display'] = 'block'  # プルダウンを表示
            total_cost += list_ex[i]['cost']
        else:
            card_styles[i]['backgroundColor'] = 'white'
            dropdown_styles[i]['display'] = 'none'  # プルダウンを非表示
        new_card_styles.append(card_styles[i])
        new_dropdown_styles.append(dropdown_styles[i])
    
    # プロジェクトIDに基づいてメンバーをフィルタリング
    filtered_members = [
        member for member in members
        if str(member["pid"]) == current_pid
    ]
    
    # タスクの割り当てと同時にメンバーのused_resourceを更新
    for i, value in enumerate(selected_values):
        if value:
            member_mid = next((member['mid'] for member in filtered_members if member['mname'] == value), None)
            if member_mid:
                task_nid = dropdown_ids[i]['nid']
                search_task = next((t for t in tasks if t.nid == task_nid), None)  # tasksからnidが一致するタスクを探す
                if search_task:
                    # 元々の割り当てを削除
                    for assignment in assignments:
                        if assignment.tid == search_task.tid:
                            member = next((member for member in filtered_members if member['mid'] == assignment.mid), None)
                            if member:
                                member['used_resource'] -= search_task.cost
                            assignments.remove(assignment)
                else:
                    # 新しいタスクを作成してtasksに追加
                    if tasks:
                        new_tid = tasks[-1].tid + 1
                    else:
                        new_tid = None
                    new_tname = list_ex[i]['name']  # 対応するカードのnameを取得
                    new_cost = list_ex[i]['cost']   # 対応するカードのcostを取得
                    new_parameter = json.dumps({"example": "value"})  # 必要に応じて適切なパラメータを設定
                    search_task = task.Task(new_tid, new_tname, task_nid, new_cost, new_parameter)
                    tasks.append(search_task)
                    ######################### 07/01
                    selected_tasks.append(search_task)
                    print('selected_taskは以下です')
                    print(selected_tasks)
                    #########################
                new_assignment = task.TaskAssignment(aid=None, tid=search_task.tid, mid=member_mid)
                assignments.append(new_assignment)
                selected_members.append(new_assignment.mid)
                member = next((member for member in filtered_members if member['mid'] == member_mid), None)
                if member:
                    member['used_resource'] += search_task.cost
                
    
    # task-tableのデータ更新
    table_data = []
    for member in filtered_members:
        assigned_tasks = []
        for assignment in assignments:
            if assignment.mid == member["mid"]:
                assigned_task_name = next((task.tname for task in tasks if task.tid == assignment.tid), "")
                if assigned_task_name:
                    assigned_tasks.append(assigned_task_name)
        
        # リストをカンマ区切りの文字列に変換
        assigned_tasks_str = ", ".join(assigned_tasks) if assigned_tasks else ""
        table_data.append({"mname": member["mname"], "AssignedTask": assigned_tasks_str})

    # member-tableのデータ更新
    member_table_data = [
        {
            "mname": member["mname"],
            "sprint_resource": member["sprint_resource"],
            "used_resource": member["used_resource"],
            "RemainingResource": member['sprint_resource'] - member['used_resource']
        }
        for member in filtered_members
    ]
    total_cost2 = 0
    x = 0
    # カードと割り当てられたタスクを比較し、割り当てられたタスクがあればカードのスタイルを変更する
    if n_clicks is not None:
        for i, card in enumerate(new_card_styles):
            card_nid = list_ex[i]['nid']  # カードのnidを取得
            for assignment in assignments:
                assigned_task = next((task for task in tasks if task.tid == assignment.tid), None)
                if assigned_task and assigned_task.nid == card_nid:
                    card['backgroundColor'] = '#d3d3d3'  # カードの背景色を変更
                    total_cost2 += assigned_task.cost
                    # 割り当て済みの人が選択されているプルダウンを表示し、選択された状態にする
                    assigned_member = next((member for member in filtered_members if member['mid'] == assignment.mid), None)
                    if assigned_member:
                        dropdown_id = {'type': 'dropdown', 'nid': card_nid}
                        dropdown_index = dropdown_ids.index(dropdown_id)
                        new_dropdown_styles[dropdown_index]['display'] = 'block'
                        new_dropdown_styles[dropdown_index]['value'] = assigned_member['mname']
                        new_dropdown_styles[dropdown_index]['placeholder'] = assigned_member['mname']
                        
    # 合計コストと残りのコストを計算する
    if x == 0:
      total_cost_mh = total_cost2
      x = 1
    else:
      total_cost_mh = total_cost
    total_sprint_resource = sum(member['sprint_resource'] for member in member_table_data)
    remaining_resource = sum(member["RemainingResource"] for member in member_table_data)
    return new_card_styles, f"Total Cost: {total_cost_mh} MH", new_dropdown_styles, table_data, member_table_data, f"メンバーの総スプリントリソース: {total_sprint_resource} MH", f"使用可能コスト残量: {remaining_resource} MH"

########################################
#####    Redmineチケットの発行     #####
########################################
def dispatch_issues(selected_pid, selected_tasks, selected_members):
    print('----------選択タスク一覧----------')
    for task_obj in selected_tasks:
       print(task_obj.tname, task_obj.nid)
    print(selected_tasks)

    # 重複したmidを削除
    seen = set()
    unique_members = []
    for member in selected_members:
        if member not in seen:
            unique_members.append(member)
            seen.add(member)
    selected_members = unique_members

    redmine_pid = 0
    print(f'pidは {selected_pid} です')
    member_redmine_id = redmine.get_redmine_ids(selected_members)
    for i, task in enumerate(selected_tasks):
        print(member_redmine_id[i], task.tname, task.nid)
        link_value = redmine.generate_link_url(selected_pid, task.nid)
        custom_fields = [{"id": 9, "value": link_value}]
        pname = redmine.get_pname(selected_pid)[0].strip()
        print(f'プロジェクト名は {pname} です')
        projects = redmine.get_projects()
        if projects:
           for project in projects:
              if project['name'] == pname:
                 redmine_pid = project['id']
        print(f'redmine_id は {redmine_pid} です')
        response = redmine.create_redmine_ticket(redmine_pid, task.tname, member_redmine_id[i], custom_fields)

    selected_tasks = []
    selected_members = []
    return response


########################################
###   非機能テストのcontentを生成    ###
########################################
def create_nft_content(sprint_num, date, uuid, catalog_id, params, input_list):
  content = {
    "status": "assigned",
    "sprint_num": sprint_num,
    "date": date,
    "uuid": uuid,
    "catalog_id": catalog_id,
  }
  # paramsとinput_listのペアをループで追加
  for param, input_value in zip(params, input_list):
      content[param] = input_value

  return content

#################################################
###   catalog_id後のパラメータデータを取得    ###
#################################################
def get_data_after_catalog_id(data):
    # catalog_idが見つかるまでのフラグ
    found_catalog_id = False
    result = {}

    # 順番に辞書を走査
    for key, value in data.items():
        # catalog_idが見つかったらその後のデータを保存する
        if found_catalog_id:
            result[key] = value
        if key == 'catalog_id':
            found_catalog_id = True

    return result
'''
selected_popover_input = []
@callback(
  Output({'type': 'radio', 'index': ALL}, 'options'),
  [Input({'type': 'popover-input', 'index': ALL}, 'value')],
  State({'type': 'buttun', 'index': ALL}, 'value'),
)
def update_radio_options(search_value, button_list):
  print('-----------------------------')
  print(f'search_value: {search_value}')
  print(f'button_list: {button_list}')
  print('-----------------------------')
  options = make_request(button_list[0], button_list[0].id)  # node.id を make_request の引数として使用する
  
  if search_value and search_value.strip():
    filtered_options = [option for option in options if search_value.lower() in option['label'].lower()]
  else:
    filtered_options = options
  
  return filtered_options
'''
@callback(
    Output('target-id-output', 'children'),
    Input({'type': 'radio', 'index': dash.dependencies.ALL}, 'value'),
    State({'type': 'radio', 'index': dash.dependencies.ALL}, 'id'),
    prevent_initial_call=True
)
def display_target_id(selected_values, radio_ids):
    if not selected_values or not radio_ids:
        return 'Select an option to see target button id'

    ctx = dash.callback_context
    if not ctx.triggered:
        return 'No selection made'

    # トリガーされた要素のIDを取得
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_index = [radio_id for radio_id in radio_ids if triggered_id in str(radio_id)][0]['index']
    
    return f'Selected value: {selected_values}, Target button id: {triggered_index}'


@callback(
  Output('model_free', 'children'),
  Output('right_free', 'children'),
  Input('select', 'value'),
  Input({'type': 'button', 'index': ALL}, 'n_clicks'),
  Input({'type': 'radio', 'index': ALL}, 'value'),
  State({'type': 'input', 'index': ALL}, 'value'),
  State({'type': 'dropdown', 'index': ALL}, 'value'),
  State('url', 'href'),
  prevent_initial_call=True
)
def up_node(input_value, button_list, radio_list, input_list, drop_list, url):
  
  print(f'input_value : {input_value}')
  print(f'button_list : {button_list}')
  print(f'radio_list : {radio_list}')
  print(f'input_list : {input_value}')
  print(f'drop_list : {drop_list}') 
  if input_value is None:
    return dash.no_update,dash.no_update
  else:
    match = re.search(r'pid=(\d+)', url)
    match1 = re.search(r'category=(\d+)', url)
    if match and match1:
      pid = match.group(1)
      category = match1.group(1)
    #settingが選ばれたとき（保守性や有効性の選択）
    #(選ばれた段階でnodeが登録されているため、修正必要)
    if (button_list == []) and (radio_list == []) and (input_list == []) and (drop_list == []):
      check_node = write_db.check_node(pid,input_value)
      
      if check_node == 'none':
        for row in df_square[e_square].values:
          if row[1] == input_value:
            write_db.write_node(pid, row[1], 'REQ', 'qiu', {'subchar': row[1], 'statement': row[2]}, 1, 0, 0)
            break
      if input_value == '保守性':
        node = node_calculation.create_tree(pid, input_value) 
      else:
        node = node_calculation.create_tree(pid, input_value, content_type='QiU') 
      
      return tree_display(node,category,pid),dash.no_update
    #トップオーバーが選択されたとき
    elif (input_list == []) and (drop_list == []):
      radio_num = [value for value in radio_list if value is not None]
      print(f'radio_num : {radio_num}')
      button_check = [value for value in button_list if value is not None] 

      ctx = dash.callback_context
      triggered_id = ctx.triggered_id
      button_id = triggered_id['index']
      print(f' button_id は {button_id}')
      global selected_pq_req 
      selected_pq_req = button_id
      print(f' selected_pq_reqは {selected_pq_req}')

      if button_check == []:
        for row in df_maintainability[e_maintainability].values:
          if row[1] == radio_num[0]:
            check_node = write_db.check_node(pid,radio_num[0])
            if check_node == 'none':
              write_db.write_node(pid, row[1], 'REQ', 'qiu', {'subchar': row[1], 'statement': row[2]}, search(category, radio_num[0]),write_db.check_node(pid, input_value)[0],0.0) 
            node = node_calculation.make_tree(pid, input_value)
            return tree_display(node,category,pid), dash.no_update
        # 保守性の場合
        for row in df_request[e_request].values:
          if row[2] == radio_num[0]:
            if row[8] == 1 or row[8] == 2:
              node1 = node_calculation.make_tree(pid, '保守性')
              node = node_calculation.add_child_to_node(node1, row[1], row[2], 1, 1, 'QRM', 'QRM')
              return tree_display(node,category,pid), dash.no_update
            else:
              result = row[9].split(',')
              for ri in df_request[e_request].values:
                for x in result:
                  if ri[7]==x:
                    check_ar = write_db.check_node(pid, ri[7])
                    check_re = write_db.check_node(pid, ri[3])     
                    if check_ar == 'none' or check_re == 'none':
                      return dash.no_update, ['QP要求文：['+ri[2]+']　'+'の品質実現または，品質活動が未設定のため，追加できません']
              node1 = node_calculation.make_tree(pid, input_value)
              node = node_calculation.add_child_to_node(node1, row[1], radio_num[0], 1, 1, 'QRM', 'QRM')
              return tree_display(node,category,pid), dash.no_update
        # 利用時品質要求の場合
        for row in df_qiu[e_qiu].values:
          if row[2] == radio_num[0]:
            check_node = write_db.check_statement(pid,radio_num[0])
            if check_node == 'none':
              write_db.write_node(pid, row[2], 'REQ', 'qiu', {'subchar': row[1], 'statement': row[2]}, 1, write_db.check_node(pid, input_value)[0],0.0, content_type=1) 
            node1 = node_calculation.make_tree(pid, input_value,'QiU')
            print(f'This is the node1: {node1}')
            #node = node_calculation.add_child_to_node(node1, node1.id, row[2], 1, 1, 'QRM')
            #print(f'This is the node: {node}')
            return tree_display(node1,category,pid), dash.no_update
        # 製品品質要求の場合
        for row in df_pq2[e_pq].values:
          if row[2] == radio_num[0]:
            check_node = write_db.check_statement(pid,radio_num[0])
            ctx = dash.callback_context
            triggered_id = ctx.triggered_id
            button_id = triggered_id['index']
            print(f' button_id は {button_id}')
            print(f'PQ check_node : {check_node}')
            if check_node == 'none':
              write_db.write_node(pid, row[2], 'REQ', 'pq', {'subchar': row[1], 'statement': row[2]}, 1, write_db.check_statement(pid, button_id)[0],0.0, content_type=1) 
            node1 = node_calculation.make_tree(pid, input_value,'QiU')
            #node = node_calculation.add_child_to_node(node1, button_id, row[2], 1, row[2], 'REQ')
            print(f'This is the node1: {node1}')
            return tree_display(node1,category,pid), dash.no_update
        return dash.no_update, message_display(radio_num[0],pid)
      # すでにあるものが選択された場合
      else:
        print(f'button_check : {button_check}')
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id
        button_id = triggered_id['index']
        print('-----------------')
        print(f'button_id : {button_id}')
        print('-----------------')
        for row in df_architecture[e_architecture].values:
          if row[3] == button_id:
            return dash.no_update, message_display(button_id,pid)
        for row in df_request[e_request].values:
          if row[3] == button_id:
            return dash.no_update, message_display(button_id,pid)
        catalogs = catalog_db.get_names_of_catalogs()
        for row in catalogs:
           if row[0] == button_id:
              return dash.no_update, message_display(button_id,pid)
        if input_value == '保守性':
          node = node_calculation.make_tree(pid, input_value)
        else:
          node = node_calculation.make_tree(pid, input_value, content_type='QiU')
        return tree_display(node,category,pid),dash.no_update
    #更新されたとき
    else:
      radio_num = [value for value in radio_list if value is not None]
      button_check = [value for value in button_list if value is not None]
      print('---------------画面右で登録が押されたとき-----------------')
      print(f'button_list : {button_list}')
      print(f'radio_list : {radio_list}')
      print(f'selected_pq_req : {selected_pq_req}')

      if button_check == []:
        return dash.no_update, dash.no_update
      ctx = dash.callback_context
      triggered_id = ctx.triggered_id
      button_id = triggered_id['index']
      if button_id[:3] == 're_':
        print(f'button_id は {button_id} です')
        print(f'button_id[:3] は {button_id[:3]} です')
        index = button_id.index('re_') + len('re_')
        print(f'index は {index} です')
        rest_of_text = button_id[index:]
        print(f'rest_of_text は [ {rest_of_text} ] です')
        input_num = [value for value in input_list if value is not None]
        if input_num == []:
          input_num += ['未記入']
        #アーキテクチャの書き込み
        for row1 in df_architecture[e_architecture].values:
          if row1[3] == rest_of_text:
            for row2 in df_request[e_request].values:
              if row2[7] == rest_of_text:
                if row2[8] == 1 :
                  child_node = write_db.check_node(pid,row2[3])
                  if child_node == 'none':
                    write_db.write_node(pid, rest_of_text, 'IMP', 'arch', {'subchar': rest_of_text, 'description': input_num[0]}, drop_list[0], write_db.check_node(pid, row1[7])[0],0.0)
                    node = node_calculation.make_tree(pid, input_value)
                    return tree_display(node,category,pid), []
                  else:
                    write_db.write_node(pid, rest_of_text, 'IMP', 'arch', {'subchar': rest_of_text, 'description': input_num[0]}, drop_list[0], write_db.check_node(pid, row1[7])[0],0.0,child_node[0])
                    node = node_calculation.make_tree(pid, input_value)
                    return tree_display(node,category,pid), []
                elif row2[8] == 2 :
                  parent_node = write_db.check_node(pid,'修正量の低減')
                  if parent_node == 'none':
                    write_db.write_node(pid, '修正量の低減', 'IMP', 'arch', {'subchar': '修正量の低減', 'description': '以下で実現'}, 1, write_db.check_node(pid, row1[7])[0],0.0)
                    write_db.write_node(pid, rest_of_text, 'IMP', 'arch', {'subchar': rest_of_text, 'description': input_num[0]}, drop_list[0], write_db.check_node(pid, '修正量の低減')[0],0.0)
                    node = node_calculation.make_tree(pid, input_value)
                    return tree_display(node,category,pid), []
                  else:
                    child_node = write_db.check_node(pid,row2[3])
                    if child_node == 'none':
                      write_db.write_node(pid, rest_of_text, 'IMP', 'arch', {'subchar': rest_of_text, 'description': input_num[0]}, drop_list[0], parent_node[0],0.0)
                      node = node_calculation.make_tree(pid, input_value)
                      return tree_display(node,category,pid), []
                    else:
                      write_db.write_node(pid, rest_of_text, 'IMP', 'arch', {'subchar': rest_of_text, 'description': input_num[0]}, drop_list[0], parent_node[0],0.0,child_node[0])
                      node = node_calculation.make_tree(pid, input_value)
                      return tree_display(node,category,pid), []
          else:
            continue
        ### 以下，品質活動 ###
        # 保守性
        for row_1 in df_request[e_request].values:
          if row_1[3] == rest_of_text:
            if row_1[8] == 1:
              parent_node =write_db.check_node(pid,row_1[7])
              if parent_node == 'none':
                write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], write_db.check_node(pid, row_1[1])[0],0.0)
                node = node_calculation.make_tree(pid, input_value)
                return tree_display(node,category,pid), []
              else:
                write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], parent_node[0],0.0)
                node = node_calculation.make_tree(pid, input_value)
                return tree_display(node,category,pid), []
            elif row_1[8]== 2:
              parent_node =write_db.check_node(pid,row_1[7])
              if parent_node == 'none':
                pare_parent_node =write_db.check_node(pid,'修正量の低減')
                if pare_parent_node == 'none':
                  write_db.write_node(pid, '修正量の低減', 'IMP', 'arch', {'subchar': '修正量の低減', 'description': '以下で実現'}, 1, write_db.check_node(pid, row_1[1])[0],0.0)
                  write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], write_db.check_node(pid, '修正量の低減')[0],0.0)
                  node = node_calculation.make_tree(pid, input_value)
                  return tree_display(node,category,pid), []
                else:
                  write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], pare_parent_node[0],0.0)
                  node = node_calculation.make_tree(pid, input_value)
                  return tree_display(node,category,pid), []
              else:
                write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], parent_node[0],0.0)
                node = node_calculation.make_tree(pid, input_value)
                return tree_display(node,category,pid), []
            else:
              write_db.write_node(pid, 'テスト自動化', 'IMP', 'arch', {'subchar': 'テスト自動化', 'description': '以下で実現'}, drop_list[0], write_db.check_node(pid, row_1[1])[0],0.0)
              write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], write_db.check_node(pid, 'テスト自動化')[0],0.0)
              node = node_calculation.make_tree(pid, input_value)
              return tree_display(node,category,pid), []
          else:
            continue

      # 以下，非機能テスト（品質活動）
      if button_id[:4] == 'nft_':
        index = button_id.index('nft_') + len('nft_')
        rest_of_text = button_id[index:]
        print(f'rest_of_text は [ {rest_of_text} ] です')
        print(f'button_id は [ {button_id} ] です')
        input_num = [value for value in input_list if value is not None]
        print(f'input_num は { input_num } です')
        print(f'pid は {pid} です')
        if input_num == []:
          input_num += ['未記入']
        ### 以下，非機能テストのDB登録 ###
        catalogs = catalog_db.get_names_of_catalogs()
        print(f'catalogs は {catalogs} です')
        for catalog in catalogs:
          if catalog[0] == rest_of_text:
            sprint_num = write_db.get_current_sprint(pid)[0]
            date = datetime.now().strftime("%Y-%m-%d")
            uid = str(uuid.uuid4())
            catalog_id = catalog_db.get_catalog_by_name(rest_of_text)[0]
            params = catalog_db.get_catalog_by_name(rest_of_text)[10].split(',')
            content_example = {'status': 'assigned', 'sprint_num': '...', 'date': '...', 'catalog_id': '...', 'para1': '...', 'para2': '...'}
            content = create_nft_content(sprint_num, date, uid, catalog_id, params, input_list)
            # if parent_node == 'none':
            write_db.write_node(pid, rest_of_text, 'ACT', 'nft', content, 1, write_db.check_statement(pid, selected_pq_req)[0], 0.0, None, content_type=2)
            node = node_calculation.make_tree(pid, input_value, 'nft')
            return tree_display(node, category, pid), []
            # else:
            #   write_db.write_node(pid, rest_of_text, 'ACT', 'sa', {'subchar': rest_of_text, 'tolerance': input_num[0]}, drop_list[0], parent_node[0],0.0)
            #   node = node_calculation.make_tree(pid, input_value)
            #   return tree_display(node,category, pid), []
            
          else:
            continue
    return dash.no_update,dash.no_update


