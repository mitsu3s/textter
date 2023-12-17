## Textter

-   A simple tweeting application modeled after X (Twitter).

## Features

-   A login system manages and displays tweets for each user.
-   As soon as a user is created, a user image is generated and displayed next to the tweet.
-   There are followers and followers, and the tweets of users you follow are also displayed on the timeline.
-   TailwindCSS is used and the design is responsive.
-   This application is under development and we do not recommend using it as a reference.

## Requirement

| Language/FrameWork | Version |
| :----------------- | ------: |
| Python             |  3.10.6 |
| Flask              |   2.2.2 |
| Flask-SQLAlchemy   |   3.0.2 |
| jinja2             |   3.1.2 |
| SQLite             |  3.39.5 |
| TailwindCSS        |   3.3.6 |

## Usage

```zsh
# Execute only during development
$ npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch

# Project execution
$ python app.py
```
