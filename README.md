# 概要
こちらはURLのみで画像を生成して取得できるというサービスになります。
現在、色やサイズを指定した無地のカラー画像を生成することが出来ます。

![impala-top](https://user-images.githubusercontent.com/101910815/226098671-fafb3963-7767-498e-8926-9210750df93e.png)

技術的には、クエリパラメータでサイズや色を指定したURLをサーバー側で処理して画像を生成し、
そのままレスポンスとして画像を返す仕組みとなっています。  

### 現在のデプロイ先URL
無し

# 使い方
例えば、以下のように画像のサイズや色を指定したURLにアクセスすると、
```
https://impala-service.watermelonman.net/api/get/?profile_type=jpeg_plain&width=512&height=128&color_rgb=146C94&quality=80
```


その指定に基づいて画像を自動で生成し、そのまま取得することが出来ます。
![sample](https://user-images.githubusercontent.com/101910815/226098832-3ee46624-597f-4ed3-bd73-607411942c2b.gif)


このようなURLをhtmlのimg要素のsrc属性に設定することで、画像を含むUIの表示テストを行うことが出来ます。
![img-src](https://user-images.githubusercontent.com/101910815/226098851-b70785e3-c226-445a-a090-1b66d86fb610.png)
![ui-test](https://user-images.githubusercontent.com/101910815/226098858-6c6584a4-3878-48e4-bed2-a2a91a370b4c.png)

### 画像URL生成ツール
また、サイトトップにアクセスしたユーザーには**画像を生成するためのURLを生成するツール**が表示されます。
こちらを利用して、使いたい画像生成用URLのベースを作成することが可能です。
![tool-sample](https://user-images.githubusercontent.com/101910815/226098897-32cfb10a-03d9-4ff8-84d9-1bb6dcb366af.gif)

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
