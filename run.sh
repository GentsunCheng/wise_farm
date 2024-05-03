#!/usr/bin/env bash
if [! -d "$(pwd)/node_modules" ]; then
  npm install
fi

sudo python transdata.py
