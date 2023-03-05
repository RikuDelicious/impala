# impala
画像生成サービスサイト

# 概要
クエリパラメータでサイズや色を指定したURLでリクエストを送るだけで画像を生成し、そのままレスポンスとして画像を返すWebアプリケーションです。  
リクエストURLは、例えば以下のようなURLになります。
```
/api/get/?format=jpeg_plain&width=512&height=512&color_rgb=3F497F&quality=75
```
このURLをHTMLのimg要素のsrc属性に指定することで、画像をダウンロードすることなくそのまま表示することが出来ます。

主な用途としては、画像を表示するUIコンポーネント等の表示テストを行う際に、  
即席のテスト画像として利用することを想定しています。（テスト画像作成の手間の削減を期待）

### 画像URL生成ツール
ユーザーに対してはフロントページとして画像URL生成ツールが表示されます。  
画像の種類（プロファイル）を選択し、プロファイル毎のフォームを入力・送信することで  
画像生成可能なURLがユーザーに対して表示されます。

# 使用技術
- フレームワーク: Django (Python)
- データベース: PostgreSQL を想定
- キャッシュ: memcached を想定
- ストレージ(生成した画像のアップロード先): AWS S3 を想定
- 一部のCSSファイル生成にtailwindcss(postcss)を利用

# ディレクトリ構成
`django-project`ディレクトリがDjangoプロジェクトのディレクトリとなります。
```
django-project/
├── api/
├── front/
├── impala/
├── manage.py
└── pytest.ini
```
プロジェクトの設定にあたるコアのパッケージは`impala/`、  
画像生成のリクエストを受けるappが`api/`、  
画像生成用のURL生成ツールを表示するappが`front/`となります。

`impala/settings/`ディレクトリ配下には環境別の設定ファイルを格納してあります。
- core.py: 全環境共通の設定
- local.py: Docker無しのローカル開発環境用の設定
- devcontainer.py: Dockerによる開発環境用の設定
- production.py: 本番環境用の設定 (デプロイ時に設定する)

# テスト
Djangoプロジェクトのコードのテストに`pytest-django`というパッケージを利用しています。  
こちらはpytestにDjango用のツールを統合したパッケージになります。  
設定ファイルは`django-project/pytest.ini`です。

各appパッケージの`tests/`ディレクトリ内にテストファイルを格納しています。  
テストを実行するには以下のコマンドを実行します。
```
cd django-project
pytest --ds=[設定モジュール名]
```
[設定モジュール名]の部分について、  
Docker無しのローカル開発環境の場合は`impala.settings.local`、  
Dockerによる開発環境の場合は`impala.settings.devcontainer`となります。

# 開発環境
### Dockerによる開発環境構築
docker composeで本番環境に近い構成で開発環境を構築できるようにしてあります。  
特に、AWS S3のモックとしてlocalstackを利用しており、
S3へのリクエストを含む処理を開発環境でテストすることができます。

サーバーのイメージ及び必要なリソースを定義したファイルは以下の通りです。
```
Root
├── Dockerfile
├── docker-compose.yml
```

さらに、Visual Studio CodeのDev Containers拡張機能からコンテナを立ち上げ、  
コンテナ内でコーディング等の作業を行うことが出来ます。  
Dev Containersの設定を記述したファイルは以下の通りです。
```
Root
├── .devcontainer
│   ├── devcontainer.json
│   └── docker-compose.yml
```

基本的には、Visual Studio Codeのコマンドパレットから以下のコマンドを実行することで  
コンテナを立ち上げて作業開始することが出来ます。  
```
> Dev Containers: Reopen in Container
```

作業開始後、Djangoの開発サーバーを立ち上げるには以下のコマンドを実行します。
```
cd django-project
python ./manage.py runserver 0.0.0.0:8000 --settings impala.settings.devcontainer
```

### Docker無しのローカル開発環境
現状は、Docker無しでDjangoの開発サーバーを立ち上げてもある程度問題なく動作するようにしてあります。  
その場合はまずPythonで仮想環境を作成して必要なパッケージをインストールする必要があります。  
(例)
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Djangoの開発サーバーを立ち上げるには以下のコマンドを実行します。
```
cd django-project
python ./manage.py runserver --settings impala.settings.local
```