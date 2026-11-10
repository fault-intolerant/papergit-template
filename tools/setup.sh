#!/bin/sh
# 新建仓库后运行一次：建虚拟环境并安装依赖，启用提交检查，运行示范检验
set -e
cd "$(git rev-parse --show-toplevel)"
PY=$(command -v python3 || command -v python)
[ -d .venv ] || "$PY" -m venv .venv
if [ -x .venv/bin/python ]; then VPY=.venv/bin/python; else VPY=.venv/Scripts/python; fi
"$VPY" -m pip install -q -r requirements.txt
git config core.hooksPath .githooks
git config commit.template .gitmessage
"$VPY" tools/lint.py
"$VPY" -m pytest -q || [ $? -eq 5 ]
echo "初始化完成。运行检验：$VPY -m pytest"
