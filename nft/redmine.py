
from psycopg2 import Error
import requests
import json
from pages.core import write_db
# Redmineの設定
REDMINE_URL = 'http://172.21.40.30:3000'
API_KEY = '6b0707f54991eefb66139cb676a64af9c38d1a5d'

# APIリクエストを行うための共通ヘッダー
headers = {'X-Redmine-API-Key': API_KEY, 'Content-Type': 'application/json'}

# チケット作成の関数
def create_redmine_ticket(pid, task_name, assigned_to_id, custom_fields):
    url = f'{REDMINE_URL}/issues.json'
    data = {
        "issue": {
            "project_id": pid,  # 適切なプロジェクトIDに置き換えてください
            "subject": task_name+'テスト',
            "assigned_to_id": assigned_to_id,
            "custom_fields": custom_fields,
            "tracker_id": 5  # 適切なトラッカーIDに置き換えてください
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

# リンクURLを動的に生成する関数
def generate_link_url(pid, node_id):
    base_url = "http://127.0.0.1:8050/qa"
    link_url = f"{base_url}?pid={pid}&node_id={node_id}"
    return link_url

# qdtのmidからredmine_idを取得
def get_redmine_ids(selected_member_ids):
    try:
        connector = write_db.get_connector()       
        cursor = connector.cursor()

        query = 'SELECT mid, redmine_id FROM member WHERE mid = ANY(%s)'
        
        cursor.execute(query, (selected_member_ids,))
        rows = cursor.fetchall()
        
        # 結果を辞書に格納
        result_dict = {mid: redmine_id for mid, redmine_id in rows}
        
        # selected_member_ids の順序を保ったまま、redmine_id のリストを作成
        result_list = [result_dict[mid] for mid in selected_member_ids if mid in result_dict]  
    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)
    finally:
        cursor.close()
        connector.close()
    return result_list

#pidからpnameを取得
def get_pname(pid):
    try:
        connector = write_db.get_connector()       
        cursor = connector.cursor()

        query = ''' 
                SELECT pname FROM project
                WHERE pid = %s;
            '''
        cursor.execute(query, (pid,))
        result = cursor.fetchone()
        message = result if result is not None else 'none'

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)
    finally:
        cursor.close()
        connector.close()
    return message

# Redmineプロジェクト情報の取得
def get_projects():
    url = f'{REDMINE_URL}/projects.json'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # エラーチェック
        projects_data = response.json()['projects']
        return projects_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None