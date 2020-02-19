#!/bin/bash

message=$1

if [ -z "$message" ]
then
  echo "Enter a commit message!"
else
  git status
  git add .
  git commit -m "$(message)"
  git push heroku master
fi
