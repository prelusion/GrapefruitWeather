#!/usr/bin/env bash

su weatherstation
git pull origin master
sudo su
docker-compose up --build
