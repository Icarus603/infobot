# InfoBot - 智能微信機器人

## 專案描述

InfoBot 是一個專為大學班長設計的智能微信機器人，用於自動化處理班內事務通知。機器人能夠：

- 實時接收多個老師的消息並自動回覆"收到！"
- 將老師的消息完整轉發給指定的同學們
- 支援macOS桌面版WeChat自動化操作
- 通過AI模型優化消息處理

## 主要功能

1. **自動回覆**：接收任何消息類型都回覆"收到！"
2. **消息轉發**：將老師消息轉發給指定學生群組
3. **多窗口管理**：同時打開多個WeChat對話窗口
4. **智能處理**：使用SiliconFlow的DeepSeek模型進行消息分析

## 技術架構

- **語言**：Python 3.10.17
- **環境管理**：Poetry + pyenv
- **UI自動化**：AppleScript + Python (適配macOS)
- **AI模型**：SiliconFlow Pro/deepseek-ai/DeepSeek-R1-0120

## 安裝與設置

### 快速安裝（推薦）

```bash
# 執行自動安裝腳本
./scripts/install_macos.sh
```

### 手動安裝

#### 1. 環境準備

```bash
# 使用pyenv設置Python版本
pyenv install 3.10.17
pyenv local 3.10.17

# 安裝系統依賴（macOS專用）
brew install cliclick

# 安裝Poetry依賴
poetry install
```

**系統依賴說明**：
- `cliclick`：macOS上的命令行鼠標控制工具，用於實現精確的雙擊操作
- 確保WeChat桌面版已安裝並可正常使用

#### 2. 配置設置

複製配置模板並填入您的資訊：

```bash
cp config/config.example.yaml config/config.yaml
```

編輯 `config/config.yaml` 文件，填入：
- SiliconFlow API Key
- 老師的微信備註名稱
- 學生的微信備註名稱

#### 3. 運行機器人

```bash
poetry run python main.py
```

## 項目結構

```
infobot/
├── infobot/                    # 主要程式碼
│   ├── __init__.py
│   ├── core/                   # 核心功能模組
│   │   ├── __init__.py
│   │   ├── bot.py             # 主機器人邏輯
│   │   ├── wechat_controller.py # WeChat控制器
│   │   └── message_handler.py  # 消息處理器
│   ├── automation/             # 自動化模組
│   │   ├── __init__.py
│   │   ├── macos_automation.py # macOS自動化
│   │   └── applescript_bridge.py # AppleScript橋接
│   ├── ai/                     # AI處理模組
│   │   ├── __init__.py
│   │   └── siliconflow_client.py # SiliconFlow API客戶端
│   └── utils/                  # 工具模組
│       ├── __init__.py
│       ├── config.py          # 配置管理
│       └── logger.py          # 日誌管理
├── config/                     # 配置文件
│   ├── config.example.yaml    # 配置模板
│   └── prompts.yaml          # AI prompt配置
├── scripts/                    # AppleScript腳本
│   ├── search_contact.scpt    # 搜索聯繫人
│   └── open_chat.scpt        # 打開對話框
├── tests/                      # 測試文件
├── logs/                       # 日誌文件
├── main.py                     # 主程式入口
├── pyproject.toml             # Poetry配置
└── README.md                  # 專案說明
```

## 注意事項

1. **權限設置**：確保給予Python和終端機輔助功能權限
2. **WeChat版本**：支援macOS桌面版WeChat，不支援網頁版
3. **穩定性**：建議在穩定的網路環境下運行

## 作者

Icarus <zhehongl91@gmail.com>

## 許可證

MIT License 