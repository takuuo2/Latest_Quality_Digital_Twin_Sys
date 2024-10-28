import re
import catalog_db

# # content データの取得
# content = catalog_db.get_content(1003)[0][0]
# print(f'content : {content}')
# catalog_id = str(content["catalog_id"])
# print(f'content_type : {type(content)}')
# print(f'catalog_id : {catalog_id}')

# # データベースから取得した算出式
# formulas = catalog_db.get_formulas(catalog_id)
# print(f'formulas : {formulas}')
# a_formula = formulas[0]
# b_formula = formulas[1]
# c_formula = formulas[2]
# print(f'a : {a_formula}, b : {b_formula}, c : {c_formula}')

# count関数: 引数の長さを返す
def count(value):
    return len(value.split(',')) if value else 0

def evaluate_formula(formula, content):
    # プレースホルダーを content の値に置き換える
    for key, value in content.items():
        placeholder = f"$({key})"
        if isinstance(value, str) and value.isdigit():
            formula = formula.replace(placeholder, value)
        else:
            formula = formula.replace(placeholder, str(value))

    print(f'置き換え後の式: {formula}') 

    # count関数を処理
    count_matches = re.findall(r'count\(\s*(.*?)\s*\)', formula)
    print(f'count_matches : {count_matches}')  
    
    for count_match in count_matches:
        # count_match の値が content に含まれる場合、カウントを適用
        count_value = count(count_match)
        formula = formula.replace(f"count({count_match})", str(count_value))

    # 式を評価
    try:
        return eval(formula)
    except Exception as e:
        print(f"計算エラー (式: {formula}): {e}")
        return None
    
def cost_calculator(nid):
    # content データの取得
    content = catalog_db.get_content(nid)[0][0]
    print(f'content : {content}')
    catalog_id = str(content["catalog_id"])
    print(f'content_type : {type(content)}')
    print(f'catalog_id : {catalog_id}')

    # データベースから取得した算出式
    formulas = catalog_db.get_formulas(catalog_id)
    print(f'formulas : {formulas}')
    a_formula = formulas[0]
    b_formula = formulas[1]
    c_formula = formulas[2]
    print(f'a : {a_formula}, b : {b_formula}, c : {c_formula}')

    # 各式を計算
    A = evaluate_formula(a_formula, content)
    B = evaluate_formula(b_formula, content)
    C = evaluate_formula(c_formula, content)
    print(f'A : {A}, B : {B}, C : {C}')

    # A, B, C の合計
    if A is not None and B is not None and C is not None:
        total = A + B + C
        print(f"計算結果 (A + B + C): {total}")
    else:
        print("計算に失敗したため、合計を計算できませんでした。")

cost_calculator(1006)