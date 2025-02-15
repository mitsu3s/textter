# Textter

- Textter は、ただ気軽につぶやけるシンプルなアプリケーションです。

## Features

- 気軽につぶやき可能
  余計な機能を省き、シンプルに投稿を楽しめます。

- 自動生成のユーザー画像
  ユーザー登録すると、プロフィール画像が自動で生成されます。

- フォロー機能
  ユーザー名を知っている場合のみフォローが可能です。
  フォローすると、自分とフォローしたユーザーの投稿をタイムラインで閲覧できます。

- フォロワーリストの閲覧
  誰にフォローされているかは、いつでも確認できます。

## Requirement

| Language/FrameWork | Version |
| :----------------- | ------: |
| Python             |  3.13.2 |
| Flask              |   3.1.0 |
| Flask-SQLAlchemy   |   3.0.2 |
| jinja2             |   3.1.2 |
| PostgresQL         |    17.3 |
| TailwindCSS        |   3.3.1 |

## Usage

```zsh
# Execute only during development
$ npx tailwindcss -i ./app/static/src/input.css -o ./app/static/dist/output.css --watch

# Project execution
$ python run.py
```
