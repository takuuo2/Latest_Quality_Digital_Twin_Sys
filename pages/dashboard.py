import dash
from dash import html, dcc, callback
from dash import Input, Output, ALL
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import json
import ast
import re
from itertools import groupby
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
from .core import write_db,node_calculation

################################################################
# 機能；カラースケールを用意
# Note:よくわからないがおいてあったためおいておく
################################################################
colors = []
for color in px.colors.qualitative.Set1:
    rgb = re.findall(r"\d+", color)
    new_rgb = []
    for val_str in rgb:
        val = int(val_str)
        val = val*2
        if val > 255:
              val = 255
        new_rgb.append(val)
    colors.append("rgb(" + ",".join(map(str, new_rgb)) + ")")

################################################################
# 機能；トレンドデータの取得
# 入力：　pid プロジェクトID, sprint_num スプリント回数
# 戻り値：　トレンドデータ
################################################################
def getTrend(pid,sprint_num):
  trend_df=[]
  data = []
  columns = ["subchar", "priority", "sprint", "achievement"]
  roots = write_db.getRoots(pid)
  for item in roots:
    subchar = item[0]['subchar']
    priority = item[2]
    achievement = item[1]
    sprint = int(sprint_num)
    data.append([subchar,priority,sprint,achievement])
    nid = item[3]
    while sprint > 1:
      sprint -= 1
      check_achivement=write_db.achievement(nid,sprint)
      if check_achivement == None:
        data.append([subchar,priority,sprint,achievement]) 
      else:
        achievement=check_achivement[0]
        data.append([subchar,priority,sprint,achievement])
  trend_df = pd.DataFrame(data=data, columns=columns)    
  df_sorted = trend_df.sort_values(by='sprint',ascending=True)
  return df_sorted

################################################################
# 機能：達成度の合計を計算
# 入力：　rend_df トレンドデータ
# 戻り値：　達成度の合計
################################################################
def SumAchievement(trend_df: pd.DataFrame):
  qiu = trend_df["subchar"].unique().tolist()
  achievement = []
  for q in qiu:
    part = trend_df[trend_df["subchar"] == q]
    max_index = part["achievement"].max()
    achievement.append([q, max_index])
  return achievement

################################################################
# 機能；達成度表示を生成
# 入力：　rend_df トレンドデータ
# 戻り値：　表示データ
################################################################
def createAchievementView(trend_df: pd.DataFrame):
  achievement = SumAchievement(trend_df)
  size = len(achievement)
  width = round(35/size)
  list_view = []

  for achieve in achievement:
    lines = trend_df[trend_df["subchar"] == achieve[0]]
    priority = lines.iat[0,1]
    achieve_decimal = Decimal(str(achieve[1])).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    view = html.Div(
      [
        html.P(achieve[0], className="qiu"),
        html.P(str(achieve_decimal) + "%", className="score")
        ],
      className="achievement_container",
      style={
        "width": str(width) + "vw",
        "font-size": str(width*0.3) + "vw",
        "color": px.colors.sequential.Blues[priority+2]
        }
      )
    list_view.append(view)
  return list_view, width

################################################################
# 機能；トレンドグラフの生成
# 入力：　rend_df トレンドデータ
# 戻り値：　トレンドグラフ
################################################################
def createTrendBar(trend_df: pd.DataFrame):
  sprint = trend_df["sprint"].nunique()
  bars = []
  lines=[]
  min = 0
  old=0.0
  for i in range(1, sprint+1):
    sprint_df = trend_df[trend_df["sprint"] == i].sort_values("priority", ascending=False).reset_index(drop=True)
    achievement = sprint_df["achievement"].reset_index(drop=True)
    achievement_new =achievement - old 
    bar = go.Bar(
      x=[sprint_df["priority"], sprint_df["subchar"]],
      y=achievement_new,
      name="sprint"+str(i),
      marker={"color": colors[i-1]}
      )
    bars.append(bar)
    old = sprint_df["achievement"].astype(float)
  trend = go.Figure(bars, layout=go.Layout(barmode="stack"))
  trend.update_layout(shapes=lines)
  trend.update_layout(
    margin=dict(t=10, b=0, l=20, r=10),
    xaxis=dict(
      dtick=1,
      title={"text": "priority"},
      categoryorder="category descending"
      ),
    yaxis=dict(
      title={"text": "achievement"}
      ),
    legend=dict(
      x=0.5,
      y=-0.2,
      xanchor="center",
      yanchor="top",
      orientation="h"
      )
    )
  return trend

################################################################
# 機能；ルートの根の探索
# 入力：　nid ノード番号
# 戻り値：　root
################################################################
def followRoot(nid):
  parent = write_db.read_parent(nid)[0]
  new_parent =0
  while parent[0] != 0:
    new_parent = write_db.read_parent(parent[0])[0]
    if new_parent[0] != 0:
      parent = new_parent
    else:
      break
  if parent[0] != 0 :
    root = write_db.check_node_nid(parent[0])
  else:
    root = write_db.check_node_nid(nid)
  return root

################################################################
# 機能；内訳データの取得
# 入力：　pid プロジェクトID
# # 戻り値：　bd_df　データセット
################################################################
def getBDAchieve(pid):
  nodes = write_db.get_nodes(pid)
  node_dic = []
  columns = ["id", "root", "parent", "label", "value", "status"]
  bd = []
  for node in nodes:
    content_dict = node[5]
    node_dic.append({"nid":node[0], "pid":node[1], "cid": node[2], "type": node[3], "subtype": node[4], 
                     "subchar": content_dict["subchar"], "content": node[5], "achievement": node[6]})
  leav = write_db.get_leaf(pid)
  leaves = node_calculation.create_leaves(leav)
  #print(leaves)
  for node in node_dic:
    parent_id = write_db.read_parent(node['nid'])[0]
    id = node['type'] + str(node['cid'])
    root = followRoot(node['nid'])[0]
    if node in leaves:
      parent = list(filter(lambda p: p['nid'] == parent_id[0], node_dic))
      parent_label = parent[0]["type"] + str(parent[0]["cid"]) + parent[0]["subchar"]
      max_score = node['achievement']
      content = node["content"]
      #print(node['type'])
      if node["type"] == "REQ":
        achievement = node['achievement']
        target = 100
      elif node["type"] == "IMP":
        achievement = node['achievement']
        target = 100
      elif node["type"] == "ACT":
        achievement = node['achievement']
        target_max = content['tolerance'][1]
        target = target_max * 100
      bd.append([id, root, parent_label, id+node["subchar"], max_score, "leaf"])
      bd.append([id, root, id+node["subchar"], id+"達成", achievement, "achieved"])
      if achievement < target:
        bd.append([id, root, id+node["subchar"], id+"未達成", target-achievement, "unachieved"]) 
      if target < max_score:
        bd.append([id, root, id+node["subchar"], id+"未着手", max_score-target, "not_started"])
    else:
      max_score = node['achievement']
      if parent_id[0] !=0:
        parent = list(filter(lambda p: p["nid"] == parent_id[0], node_dic))
        parent_label = parent[0]["type"] + str(parent[0]["cid"]) + parent[0]["subchar"]
        bd.append([id, root, parent_label, id+node["subchar"], max_score, "parent"])
      else:
        bd.append([id, root, root, id+node["subchar"], max_score, "root"])
  bd_df = pd.DataFrame(data=bd, columns=columns)
  #print(bd_df)
  return bd_df

################################################################
# 機能；内訳グラフの作成
# 入力：　bd_df　データセット，pid プロジェクトID
# # 戻り値：　bd_graph graphのデータ
#Note：ここがうまく表示できない原因だと思う
################################################################
def createBDGraph(bd_df: pd.DataFrame,pid):
  roots = write_db.getRoots(pid)
  priority_dic = node_calculation.calcQiUPriority(roots)
  sorted_priority = sorted(priority_dic, key=lambda x:x['priority'], reverse = True)
  bd_graph = []
  width = 60 / len(priority_dic)
  i = 0
  for k in sorted_priority:
    bd_qiu = pd.DataFrame(bd_df[bd_df["root"] == k["key"]])
    root = pd.Series({"id": "root", "root": k["key"], "parent": "", "label": k["key"], "value": 100.0})
    bd_data = pd.concat([bd_qiu, root.to_frame().T], ignore_index=True)
    icicle = px.icicle(
      names=bd_data["label"],
      parents=bd_data["parent"],
      values=bd_data["value"],
      branchvalues="total",
      color=bd_data["status"],
      color_discrete_map={"root": "royalblue", "parent": "deepskyblue", "leaf": "darkorange","achieved": "springgreen", "unachieved": "red", "not_started": "white"},
      hover_name=bd_data["id"],
      hover_data=[bd_data["id"], bd_data["status"]]
      )
    icicle.update_traces(
      root_color="lightgrey",
      sort=False
      )
    icicle.update_layout(
      margin={"l": 0, "r": 0, "t": 20, "b": 0}
      )
    bd_graph.append(
      dcc.Graph(
        figure=icicle,
        style={
          "width": str(width) + "vw" ,
          "height": "50vh"
          },
        id={"type": "breakdown", "index": i},
        )
      )
    i += 1
  return bd_graph

################################################################
# 機能；テストデータを取得
# 入力：　pid プロジェクトID, sprint_num 現在のスプリント回数
# # 戻り値：　test_df  テストデータセット
#Note：
################################################################
def getTestData(pid,sprint_num):
  nodes = write_db.get_nodes_type(pid)
  test_list = []
  columns = ["data", "id", "type", "subchar","borderline", "upper", "target"]
  for node in nodes:
    id = node[3] + str(node[2])
    content = node[5]
    sprint_result = []
    if node[3] == "ACT":
      for x in range(1,int(sprint_num)):
        result = write_db.check_achievement(pid,content['subchar'],x)
        sprint_result.append([x, result])
      sprint_result.append([int(sprint_num), node[6]])
      test_list.append([sprint_result, id, node[3], content['subchar'], content["tolerance"][0], content["tolerance"][1], (content["tolerance"][0]+content["tolerance"][1])/2])
    elif node[3] == "IMP":
      for x in range(1,int(sprint_num)):
        result = write_db.check_achievement(pid,content['subchar'],x)
        sprint_result.append([x, result])
      sprint_result.append([int(sprint_num), node[6]])
      test_list.append([sprint_result, id, node[3], content["subchar"], 1.0, 1.0, 1.0])
  test_df = pd.DataFrame(data=test_list, columns=columns)
  
  return test_df

################################################################
# 機能；テスト結果のグラフを生成
# 入力：　test_df データセット
# # 戻り値：　testgraph  グラフデータ
#Note：
################################################################
def createTestGraph(test_df):
    testgraph = {}
    for index, row in test_df.iterrows():
        result = row[0]
        if row[4] == row[5] and row[4] == row[6]:
            df = pd.DataFrame(result, columns=["x", "y"]),
            figure = go.Figure(
                go.Bar(
                    x=df[0]["x"],
                    y=df[0]["y"]
                )
            )
            figure.update_layout(title = row[3])
        else: 
            df = pd.DataFrame(result, columns=["x", "y"])
            figure = go.Figure(
                go.Scatter(
                    x=df["x"],
                    y=df["y"],
                    mode="markers+lines"
                )
            )
            figure.update_layout(
                shapes=[
                    go.layout.Shape(
                        type="rect",
                        xref="paper",
                        yref="y",
                        x0=0,
                        x1=1,
                        y0=row[4],#lower
                        y1=row[6],#target
                        fillcolor="#FECB52",
                        layer="below",
                        line={"width": 0},
                    ),
                    go.layout.Shape(
                        type="rect",
                        xref="paper",
                        yref="y",
                        x0=0,
                        x1=1,
                        y0=row[6],#target
                        y1=row[5],#upper
                        fillcolor="#B6E880",
                        layer="below",
                        line={"width": 0},
                    )
                ],
                title = row[3],
                # xaxis={"title": {"text": x_label}},
                # yaxis={"title": {"text": y_label}},
                legend=dict(xanchor='left',
                    yanchor='bottom',
                    x=0.02,
                    y=1.02,
                    orientation='h',
                ),
                plot_bgcolor="#fb8072"
            )
        testgraph[row[1]] = figure
    return testgraph


################################################################
# 機能；ノード一覧データ作成
# 入力：　pid プロジェクトID, sprint_num 現在のスプリント回数
# # 戻り値：　table_df ノードのtableデータ, root_dic　親のデータ
#Note：
################################################################
def getTableData(pid,sprint_num):
  nodes =  write_db.get_nodes(pid)
  node_list = []
  root_dic = {}
  columns = ["rootid", "type", "cid", "subtype", "subchar", "statement", "achievement", "status"]
  for node in nodes:
    content = node[5]
    root = followRoot(node[0])[0]
    root = write_db.check_node(pid, root)[0]
    if node[3] == "REQ":
      target = 100.0
      achievement = node[6]
      status = "Unachieved"
      if achievement == 100:
        status = "Achieved"
      elif achievement >= target:
        status = "Sprint Achieved"
      node_list.append([root, node[3], node[2], node[4], content["subchar"], content["statement"], 
                achievement, status])# rootid type, cid, subtype, subchar, statement, achievement, status
    elif node[3] == "IMP":
      target = 100.0
      achievement = node[6]
      status = "Unachieved"
      if achievement == 100:
        status = "Achieved"
      elif achievement >= target:
        status = "Sprint Achieved"
      node_list.append([root, node[3], node[2], node[4], content["subchar"], content["description"], 
                        achievement, status])
    elif node[3] == "ACT":
      if node[6] != 0.0:
        target_test = node[6]
        rating = node[6]*0.01
      else:
        target_test = -1.0
        rating = 0.0
      status = "Unachieved"
      if content["tolerance"][0] > content["tolerance"][1]:
        if target_test <= content["tolerance"][0] and target_test > (content["tolerance"][0]+content["tolerance"][1])/2:
          rating_target = 0.7
        elif target_test <= (content["tolerance"][0]+content["tolerance"][1])/2:
          rating_target = 1.0
        else:
          rating_target = 0.0
      else:
        if target_test >= content["tolerance"][0] and target_test < (content["tolerance"][0]+content["tolerance"][1])/2:
          rating_target = 0.7
        elif target_test >= (content["tolerance"][0]+content["tolerance"][1])/2:
          rating_target = 1.0
        else:
          rating_target = 0.0
      if rating == 1.0:
        status = "Achieved"
      elif rating >= rating_target:
        status = "Sprint Achieved"
      node_list.append([root, node[3], node[2], node[4], content["subchar"], "", 
                rating*100, status])
    root_dic[node[3]+str(node[2])] = root
  table_df = pd.DataFrame(data=node_list, columns=columns)     
 # print(root_dic)
  #print(table_df)
  return table_df, root_dic
  
################################################################
# 機能；ノード一覧表を作成
# 入力：　table_df　ノードのtableデータ，pid プロジェクトID
# # 戻り値：　tables テーブルのデータ
#Note：
################################################################
def createTables(table_df,pid):
    roots = write_db.get_Roots(pid)
    root_dic = []
    for  node in roots:
      content_dict = node[5]
      root_dic.append({"nid":node[0], "pid":node[1], "cid": node[2], "type": node[3], "subtype": node[4], 
                      "subchar": content_dict["subchar"], "content": node[5], "achievement": node[6]})
    root_dic.sort(key=lambda x: x["nid"])
    keys = [k for k, g in groupby(root_dic, key=lambda x: x["nid"])]
    tables = {} 
  
    for k in keys:
        table_data = pd.DataFrame(table_df[table_df["rootid"] == k])
        table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in table_data.columns if i != "rootid"],
            data=table_data.to_dict("records"),
            style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            },
            style_data_conditional=[
            {
                'if': {
                    'filter_query': '{status} = "Achieved"',
                },
                'backgroundColor': 'springgreen',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{status} = "Sprint Achieved"',
                },
                'backgroundColor': 'royalblue',
                'color': 'white'
            },
            {
                'if': {
                    'filter_query': '{status} = "Unachieved"',
                },
                'backgroundColor': 'red',
                'color': 'white'
            },
            ]
        )
        tables[k] = table
    return tables

################################################################
# 機能；ダッシュボード画面のレイアウト
# 入力：　pid プロジェクトID, sprint_num スプリント回数
# 戻り値：　レイアウト
################################################################
def dashboard_layout(params):
  global testgraph
  global root_dic
  global tables
  pid = params.get('pid')
  sprint_num = params.get('sprint_num')
  category_num = params.get('category')
  testgraph = {}
  root_dic = {}
  tables = {}
  trend_df = getTrend(pid,sprint_num)
  trend = createTrendBar(trend_df)
  achievement, achieve_width = createAchievementView(trend_df)
  bd_df = getBDAchieve(pid)
  bd_graph = createBDGraph(bd_df,pid)
  test_df = getTestData(pid,sprint_num)
  testgraph = createTestGraph(test_df)
  table_df, root_dic = getTableData(pid,sprint_num)
  tables = createTables(table_df,pid)
  return html.Div(
    [
      #左側
      html.Div(
        [
          #達成度
          html.Div(
            achievement,
            style={
              'display': 'flex',
              'flex-direction': 'row',
              'justify-content': 'space-around',
              'align-items': 'stretch',
              'padding-left': '5%'
              }
            ),
          html.Div(
            [
              dcc.Graph(
                figure=trend,
                style={
                  'height': '100%',
                  'margin': '5% '
                  },
                )
              ],
            style={'height': '60%'}
            ),
          ],
        className='left'
        ),
          
      #右側
      html.Div(
        [
          #内訳
          html.Div(
            bd_graph,
            className='bd',
            ),
          #テスト
          html.Div(
            [
              dcc.Graph(
                id='test',
                style={
                  'height': '50vh',
                  'width': '50%'
                  }
                ),
              html.Div(
                id='table',
                style={
                  'height': '50vh',
                  'width': '50%',
                  }
                )
              ],
            className='bottom'
            )
          ],
        className='right'
        )
      ],
    style={
      'display': 'flex'
      }
    )

@callback(
    Output("test", "figure"),
    Input({"type": "breakdown", "index": ALL}, "clickData"),
    prevent_initial_call=True
)
def showTestGraph(clickData):
    if clickData:
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]["value"] is None:
            return "No clicks yet"
        else:
             # IDに指定した文字列を受け取る
            clicked_id_text = ctx.triggered[0]['prop_id'].split('.')[0]
            # 文字列を辞書に変換する
            clicked_id_dic = ast.literal_eval(clicked_id_text)
            # クリックした番号を取得
            clicked_index = clicked_id_dic['index']
        
        hovername = [data["hovertext"] for data in clickData[clicked_index]["points"]]
        if hovername[0] != "(?)":
            figure = testgraph.get(hovername[0])
            if figure:
                return figure
        raise dash.exceptions.PreventUpdate


@callback(
    Output("table", "children"),
    Input({"type": "breakdown", "index": ALL}, "clickData"),
    prevent_initial_call=True
)
def showTables(clickData):
    if clickData:
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]["value"] is None:
            return "No clicks yet"
        else:
             # IDに指定した文字列を受け取る
            clicked_id_text = ctx.triggered[0]['prop_id'].split('.')[0]
            # 文字列を辞書に変換する
            clicked_id_dic = ast.literal_eval(clicked_id_text)
            # クリックした番号を取得
            clicked_index = clicked_id_dic['index']
        
        hovername = [data["hovertext"] for data in clickData[clicked_index]["points"]]
        if hovername[0] != "(?)":
            root_id = root_dic.get(hovername[0])
            if root_id is not None:
                table = tables[root_id]
                return table
        raise dash.exceptions.PreventUpdate