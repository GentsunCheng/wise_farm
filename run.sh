#!/usr/bin/env bash
ws = $(pwd)
if [! -d "${ws}/node_modules" ]; then
  npm install
fi
cd "${ws}/app"
sudo python transdata.py
cd "${ws}"
