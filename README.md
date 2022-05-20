## face_recognition system

顔認証システムをWebに組み込んだものです。データセットを行い、学習、トレーニングデータを使用することで実際に顔認証を行います。

## コードの実行方法

`cd face_recognition`でface_recognitionのディレクトリに移動し、`python manage.py runserver`を入力することでサーバーを立ち上げ、実行することが可能です。

## 詳細設定

```
pip install -r requirements.txt
createdb 〇〇
python manage.py makemigrations
python manage.py manage.py
```

上記はPostgresSQLのデータベースを作成し、ミグレーションを行うまでの流れです。

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DB名',
        'USER': 'PCのユーザー名',
        'PASSWORD': 'PCのパスワード',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
`settings.py`にある上記のコードに任意の変更を加えてください。

## 仕様

Webに顔認証システムを組み込んだもので、Webからカメラの起動を行い、自身の顔のデータを撮ります。そのデータを基にして学習を行い、実際に顔認証を行うというものです。

## 問題点

- Webのストリーミング通信を使用しているが作動しない時がある
- 学習結果とデータセットの画像の枚数が少ない
- 顔認証一致度の向上が必要である

## 要件定義

- カメラの起動
- 写真を撮影する
- 動画の起動
- 学習
- データセット
- 実装
- これらの機能を有する

## 外部設計

- カメラ機能の出力を画面上に出力する単純なもの

## 内部設計

- カメラでユーザーの顔の画像をデータセットとして保存
- ユーザー名と共に学習を行う
- 学習後カメラを起動させるとユーザーの名前が表示される
- 顔認証に成功していなかった場合にはUnknownが表示される

## 活用

- コロナ禍もあってマスクをしているかどうか判別したい
- 保育園や幼稚園などの安全性が必要な場所への利用を考えたかった

## 開発

GithubのソースやWebサイトの情報を頼りに開発を行いました。