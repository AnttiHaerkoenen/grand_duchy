#!/bin/bash

appname=$1

if [ -z "$appname" ]
then
  echo "Enter a valid name for the app!"
else
  git init
  virtualenv venv
  source venv/bin/activate

  pip install dash plotly pandas gunicorn

  echo "venv" > .gitignore
  echo "*.pyc" >> .gitignore
  echo ".DS_Store" >> .gitignore
  echo ".env" >> .gitignore

  echo "web: gunicorn app:server" > Procfile

  pip freeze > requirements.txt
  sed -i '/pkg-resources/d' requirements.txt

  heroku create "$appname" --region eu

  git add .
  git commit -m "First commit"
  git push heroku master
  heroku ps:scale web=1
fi
