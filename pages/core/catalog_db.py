import psycopg2
from psycopg2 import Error
import json

#########################################################
# 機能： QDTデータベースのコネクションを得る（内部関数）
# Note：研究室サーバのpostresql/QDT-DBデータベースを固定
#      して使用
#########################################################
def get_connector():
  connector = psycopg2.connect(
    'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
      user = 'postgres',        
      password = 'selab',  
      host = '172.21.40.30',  
      port = '5432',           
      dbname = 'QDT-DB'
    )
  )
  return connector

#########################################################
# 機能：   カタログ情報の取得
# 入力：   nid ノードのid
# 戻り値： 引数nidであるノードのcontent内catalog_idのレコード（リスト）のリスト
#########################################################
def get_catalog(nid):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT catalog.*
            FROM catalog
            JOIN (
                SELECT CAST(content->>'catalog_id' AS INTEGER) AS extracted_catalog_id
                FROM qualitynode
                WHERE nid = %s
            ) AS extracted
            ON catalog.id = extracted.extracted_catalog_id;
        '''
        cursor.execute(info, (nid,))
        result = cursor.fetchall()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   カタログ情報の取得
# 入力：   TreeNodeクラスのsubtype(副特性)
# 戻り値： 引数subtypeを持つレコード（リスト）のリスト
#########################################################
def get_catalog_by_subchar(subchar):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT name, overview
            FROM catalog
            WHERE target_qc = %s;
        '''
        cursor.execute(info, (subchar,))
        result = cursor.fetchall()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   カタログ情報の取得
# 入力：   なし
# 戻り値： DBにあるカタログレコード（リスト）のリスト
#########################################################
def get_names_of_catalogs():
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT name
            FROM catalog;
        '''
        cursor.execute(info,)
        result = cursor.fetchall()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   カタログ情報の取得
# 入力：   テストの名前
# 戻り値： DBにあるカタログレコード（リスト）のリスト
#########################################################
def get_catalog_by_name(name):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT *
            FROM catalog
            WHERE name = %s;
        '''
        cursor.execute(info,(name,))
        result = cursor.fetchone()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   カタログ情報の取得
# 入力：   テストの名前
# 戻り値： DBにあるカタログレコード（リスト）のリスト
#########################################################
def get_catalog_by_id(id):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT *
            FROM catalog
            WHERE id = %s;
        '''
        cursor.execute(info,(id,))
        result = cursor.fetchone()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   nodeのcontent取得
# 入力：   nid ノードのid
# 戻り値： 引数nidであるノードのcontentのレコード
#########################################################
def get_content(nid):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT content
            FROM qualitynode
            WHERE nid = %s;
        '''
        cursor.execute(info, (nid,))
        result = cursor.fetchall()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   カタログのパラメータ取得
# 入力：   テストの名前
# 戻り値： DBにあるカタログのパラメータ情報
#########################################################
def get_params_by_name(name):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT parameter
            FROM catalog
            WHERE name = %s;
        '''
        cursor.execute(info,(name,))
        result = cursor.fetchone()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result

#########################################################
# 機能：   JSONからカタログの名前取得
# 入力：   content（JSONデータ）
# 戻り値： DBにあるカタログの名前
#########################################################
def get_catalog_name_by_json(data):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        catalog_id =  data.get('catalog_id')
        info = '''
            SELECT name
            FROM catalog
            WHERE id = %s;
        '''
        cursor.execute(info,(catalog_id,))
        result = cursor.fetchone()
        print(f' result : {result[0]}')

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result[0]


#########################################################
# 機能：   カタログ情報の取得
# 入力：   なし
# 戻り値： DBにあるカタログレコード（リスト）のリスト
#########################################################
def get_catalogs():
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT *
            FROM catalog;
        '''
        cursor.execute(info,)
        test_data = cursor.fetchall()

        # カラム名を取得
        colnames = [desc[0] for desc in cursor.description]
        
        # 辞書形式に変換
        test_data_dict = [dict(zip(colnames, row)) for row in test_data]

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return test_data_dict


#########################################################
# 機能：ノードのcontentを取得
# 入力： カタログ情報７項目，算出３式
# 戻り値： None
#########################################################
def update_catalog(summary, quality_characteristic, purpose, target, 
                   execution_steps, calculation_method, result, 
                   a_formula, b_formula, c_formula, catalog_id):
  try:
    connector = get_connector()    
    cursor = connector.cursor() 

    update_query = '''
                    UPDATE catalog 
                    SET overview = %s, target_qc = %s, description = %s, test_object = %s,
                    procedure = %s, meas_func = %s, test_result = %s,
                    prep_cost = %s, testing_cost = %s, analysis_cost = %s

                    WHERE id = %s;
                  '''
    cursor.execute(update_query, (summary, quality_characteristic, purpose, target, 
                   execution_steps, calculation_method, result, 
                   a_formula, b_formula, c_formula, catalog_id))
    connector.commit() 
        
  except (Exception, Error) as error:
    print('PostgreSQLへの接続時のエラーが発生しました:', error)

  finally:
    cursor.close()
    connector.close()

  return None


#########################################################
# 機能：   カタログのパラメータ取得
# 入力：   テストの名前
# 戻り値： DBにあるカタログのパラメータ情報
#########################################################
def get_formulas(id):
    try:
        connector = get_connector()
        cursor = connector.cursor()
        
        info = '''
            SELECT prep_cost, testing_cost, analysis_cost
            FROM catalog
            WHERE id = %s;
        '''
        cursor.execute(info,(id,))
        result = cursor.fetchone()

    except (Exception, Error) as error:
        print('PostgreSQLへの接続時のエラーが発生しました:', error)

    finally:
        cursor.close()
        connector.close()

    return result