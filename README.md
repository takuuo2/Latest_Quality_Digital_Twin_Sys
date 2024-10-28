# quality-digital-twin
## 目次

- [インストール](#インストール)
- [実行](#実行)
- [注意事項](#注意事項)

## インストール

### 必要条件

- Python 
- Git

### インストール手順

1. リポジトリをクローンする。  
    `
    git clone https://github.com/flccr/quality-digital-twin.git
    `

2. 必要なパッケージをインストールする。  
    `
    pip install dash 
    `  
    など実行に必要なパッケージをインストール


## 実行

### 実行手順

1. プロジェクトのディレクトリに移動  
    `
    cd quality-digital-twin
    `

2. 以下のコマンドを実行（大学ネットワークに入ってから）  
    `
    python app.py
    `  
    ※ここで実行できない場合は，必要なパッケージがインストールされていないことが原因

3. ブラウザで `http://127.0.0.1:8050` にアクセス  
    以下の （### 機能/ページURL ）で示すURLにもクエリパラメータを指定することでアクセス可能  

### 機能/ページURL
※ pid=156のプロジェクトを例としたURLを記載  

``` 例   
[ 画面名 ] ( ページURL )  
- できること  
```       

[ ホーム ] ( http://127.0.0.1:8050 or http://127.0.0.1:8050/home )
- プロジェクトの作成
- スプリントの状況を更新
- 各ページへの遷移

[ 編集 ] ( http://127.0.0.1:8050/edit?project_name=1026_test&category=2&sprint_num=1&state=planning%20%20&pid=156 )
- 品質状態モデルの編集
- スプリント計画

[ データ参照 ] ( http://127.0.0.1:8050/db?&pid=156 )
- 指定プロジェクトのデータ参照

[ カタログ一覧 ] ( http://127.0.0.1:8050/catalog )
- カタログの一覧参照

[ カタログ詳細 ] ( http://127.0.0.1:8050/catalog/details/{catalog_id} )
- カタログの詳細参照

[ カタログ編集 ] ( http://127.0.0.1:8050/catalog/edit/{catalog_id} )
- カタログの編集


## 注意事項

1. supportテーブルのsontributionでfloat[0,1]ではなく、integer[0,3]


```
・実行方法
app.pyを実行してください。
➀プロジェクト名＆カテゴリを入力
➁現在のスプリント(`current state`)を1以上に変更することにより、各メニュー（Create Category以外）のボタンを押すことが可能
※Create Categoryはプロジェクト名などを入力しなくても押すことが可能

・各ボタン
Sprint Planning: 品質状態モデルの編集/表示
Dashboard: ダッシュボートの表示（現在、スプリントの達成度のみ表示可能）
QDT-DB: 指定したプロジェクトの情報表示（nodeなどのデータ）
Create Category: QC-DB.db（各重要度のデータベース）を作成
```

