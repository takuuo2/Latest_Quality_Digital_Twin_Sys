import pandas as pd
import dash
from dash import html
import pandas as pd

from pages.core import catalog_db
from. import write_db

e_base2 = 'QiU要求+PQ要求.xlsx'
e_qiu = 'QiUR'
e_pq = 'PQR'

df_qiu = pd.read_excel(e_base2, sheet_name=[e_qiu])
df_pq = pd.read_excel(e_base2, sheet_name=[e_pq])

#ノードを定義 
class TreeNode:
    def __init__(self, id, contribution, other, type, subtype):
        self.id = id
        self.contribution = contribution
        self.other = other
        self.type = type
        self.subtype = subtype
        self.children = []
        self.parent = None
    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self
    def is_leaf(self):
        return len(self.children) == 0
    def __str__(self):
        parent_id = self.parent.id if self.parent else None
        children_ids = [child.id for child in self.children]
        return f"Node: {self.id}, Contribution: {self.contribution}, Parent: {parent_id}, Children: {children_ids}, Other: {self.other}, Type: {self.type}, SubType: {self.subtype}"
'''
木構造の作成
ノードのツリー構造を作成し、ツリーのルートを返す
'''
def create_tree(pid,parent_node_value, content_type=None, parent_node=None):
  print('-------- create_treeの始まり --------')
  print(f'content_type : {content_type}')
  print(f'parent_node : {parent_node}')
  if parent_node_value in {'有効性', '効率性', '満足性', 'リスク回避性', '利用状況網羅性'}:
    aim_node = write_db.check_node(pid,parent_node_value)
  else:
    aim_node = write_db.check_node(pid,parent_node_value)
  for row in df_qiu[e_qiu].values:
    if row[2] == parent_node_value:
      aim_node = write_db.check_statement(pid,parent_node_value)
  for row in df_pq[e_pq].values:
    if row[2] == parent_node_value:
      aim_node = write_db.check_statement(pid,parent_node_value)
  catalogs = catalog_db.get_names_of_catalogs()
  
  print(f'aim_node : {aim_node}')
  if aim_node !='none':
    child_nodes=write_db.make_child(aim_node[0]) # データベースから子ノードを取得
    if parent_node is None:
      parent_node = TreeNode(parent_node_value, 1, aim_node[5], aim_node[3], aim_node[4])
    
    if child_nodes != []:
      for row in child_nodes:
        contribution=row[2]
        type=row[0]
        subtype=row[3]
        if content_type == None:  #保守性の場合
          id= row[1]['subchar']
          if type=='REQ':
            other=row[1]['statement']
          elif type == 'IMP':
            other=row[1]['description']
          else:
            other=row[1]['tolerance']  
        else:  #保守性以外の場合
          if 'statement' in row[1]:
            id = row[1]['statement']
          else:
            id = row[1]['uuid']
          
          if type=='REQ':
            other=row[1]
          elif type == 'IMP':
            other=row[1]['description']
          else:
            other=row[1]
        node = TreeNode(id, contribution, other, type, subtype)
        
        parent_node.add_child(node)
        print(f'Creating Tree. Node id:{id}, contribution:{contribution}, other:{other}, type:{type}, subtype:{subtype}')
        create_tree(pid, id, content_type, node)
  else:
    parent_node='none'
  return parent_node


#貢献度が０のやつを抜いて作り変える
def remove_zero_contribution(node):
  if node is None:
    return None
  updated_children = []
  # 子ノードの貢献度が0でないもの、または子ノードがない場合を抽出
  for child in node.children:
    updated_child = remove_zero_contribution(child)
    if updated_child and updated_child.contribution != 0:
      updated_children.append(updated_child)
    else:
      if updated_child:
        for grandchild in updated_child.children:
          node.add_child(grandchild) 
  node.children = updated_children
  # 貢献度が0の親ノードを削除し、その子ノードを親の親ノードに関連付ける
  if node.contribution == 0 and not any(child.contribution != 0 for child in node.children):
    return None
  else:
    return node

#木構造を作成
def make_tree(pid,root_node_id, content_type=None):
  root_node = create_tree(pid,root_node_id, content_type)
  if root_node !='none':
    updated_root = remove_zero_contribution(root_node)
  else:
    updated_root ='none'
  return updated_root

#表示する
def print_tree(node, indent=''):
  if node is None:
    return  
  print(f'{indent}ID:{node.id}, 貢献度: {node.contribution}, 他: {node.other},タイプ:{node.type}')
  for child in node.children:
    print_tree(child, indent + '  ')
    
'''
既存のツリーに新しい子ノードを追加し、追加したあとのルートノードを返す
'''
def add_child_to_node(existing_root_node, parent_node_id, new_node_id, new_node_contribution, new_node_other, new_node_type, new_node_subtype):
  # デバッグプリントの追加
  print(f'Existing root node: {existing_root_node}')
  print(f'Parent node ID: {parent_node_id}')
  print(f'New node ID: {new_node_id}')
  print(f'New node contribution: {new_node_contribution}')
  print(f'New node other: {new_node_other}')
  print(f'New node type: {new_node_type}')
  print(f'New node subtype: {new_node_subtype}')

  def add_child_to_specific_node(node):
    
    if node.id == parent_node_id:
      new_node = TreeNode(new_node_id, new_node_contribution, new_node_other, new_node_type, new_node_subtype)
      node.add_child(new_node) 
      return existing_root_node  
    for child in node.children:
      updated_child = add_child_to_specific_node(child)
      if updated_child:
        return existing_root_node
    return None
  return add_child_to_specific_node(existing_root_node)

########
#追加 島田くん
########

# 品質特性ごとの重要度を算出する
def calcQiUPriority(roots: list):
  priority_dic = []
  for node in roots:
    priority_dic.append({"key": node[0]['subchar'], "priority": node[2]})
  return priority_dic

################################################################
# 機能；葉のデータセット作成
# 入力：　leav　葉のデータ
# 戻り値：　data 葉のデータセット
################################################################
def create_leaves(leav):
  data = []
  for root in leav:
    content =root[5]
    data.append({"nid":root[0], "pid":root[1], "cid": root[2], "type": root[3], "subtype": root[4], 
        "subchar": content["subchar"], "content": root[5],'achievement':root[6]})
  return data