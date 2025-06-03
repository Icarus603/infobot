#!/bin/bash

# InfoBot macOS 安裝腳本
# 作者: Icarus <zhehongl91@gmail.com>

set -e  # 遇到錯誤立即退出

echo "🚀 開始安裝 InfoBot (macOS)"
echo "================================"

# 檢查是否為 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此腳本僅適用於 macOS 系統"
    exit 1
fi

# 檢查 Homebrew 是否安裝
if ! command -v brew &> /dev/null; then
    echo "❌ 請先安裝 Homebrew: https://brew.sh/"
    exit 1
fi

# 檢查 pyenv 是否安裝
if ! command -v pyenv &> /dev/null; then
    echo "⚠️  pyenv 未安裝，正在通過 Homebrew 安裝..."
    brew install pyenv
fi

# 檢查 Poetry 是否安裝
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry 未安裝，正在安裝..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

echo "📦 安裝系統依賴..."

# 安裝 cliclick（用於 macOS 雙擊操作）
if ! command -v cliclick &> /dev/null; then
    echo "📥 安裝 cliclick..."
    brew install cliclick
else
    echo "✅ cliclick 已安裝"
fi

echo "🐍 設置 Python 環境..."

# 安裝 Python 3.10.17
if ! pyenv versions | grep -q "3.10.17"; then
    echo "📥 安裝 Python 3.10.17..."
    pyenv install 3.10.17
fi

# 設置本地 Python 版本
pyenv local 3.10.17

echo "📚 安裝 Python 依賴..."

# 安裝 Poetry 依賴
poetry install

echo "⚙️  配置檢查..."

# 檢查配置文件
if [ ! -f "config/config.yaml" ]; then
    if [ -f "config/config.example.yaml" ]; then
        echo "📋 複製配置模板..."
        cp config/config.example.yaml config/config.yaml
        echo "⚠️  請編輯 config/config.yaml 填入您的配置信息"
    else
        echo "❌ 未找到配置模板文件"
    fi
else
    echo "✅ 配置文件已存在"
fi

echo ""
echo "🎉 安裝完成！"
echo "================================"
echo ""
echo "接下來的步驟："
echo "1. 編輯配置文件: config/config.yaml"
echo "2. 確保 WeChat 桌面版已安裝並登錄"
echo "3. 運行機器人: poetry run python main.py"
echo ""
echo "重要提醒："
echo "- 需要在「系統偏好設定 → 安全性與隱私 → 輔助功能」中給予終端機權限"
echo "- 確保 WeChat 處於前台並可正常使用"
echo "" 