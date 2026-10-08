# 🛡️ 異地備援與測試異常日誌擷取系統 (Log Capture & Render Pipeline)

這是一個全自動化的日誌擷取與截圖工具。系統會自動掃描測試案例（Cases）中的 Email 與 Log 檔案，精準抓取異常訊息（如 `ERROR`, `FATAL`, `500` 等），並將其轉換為**現代化、高質感的企業級警報卡片截圖**，方便直接貼入驗收報告中。

---

## ✨ 系統特色

- 🔍 **智慧日誌追蹤**：優先尋找附件 `.log` 檔，若無附件則自動降級（Fallback）掃描 Email 內文。
- 🎨 **現代化警報卡片**：使用 Playwright 進行無頭瀏覽器截圖，產出具備圓角、陰影、自適應寬度的高清 PNG，取代醜陋的純文字截圖。
- 🛡️ **高健壯性設計**：內建 HTML 防跳脫處理（防 XSS 破壞版面）、非同步字體載入等待、以及支援跨目錄安全執行的絕對路徑架構。
- 🧱 **高度解耦架構**：將「資料擷取」與「畫面渲染」徹底分離，中間透過統一的 JSON 檔案溝通，極大化未來的擴充性。

---

## 📂 專案目錄結構

```text
📦 專案根目錄
├── 📂 input/               # 📥 放入測試案例的原始檔案
│   ├── 📂 case01/          # 每個資料夾代表一個獨立的案例
│   │   ├── email_01.md     # 測試結果 Email 內文 (Markdown 格式)
│   │   └── login_error.log # (可選) 實體的錯誤日誌檔
│   └── 📂 _template/       # 供您快速複製建立新案例的範本
├── 📂 output/              # 📤 自動產出的報告與精美截圖
│   ├── case01_report.html
│   └── case01_report.png
├── 📂 processed/           # ⚙️ 系統自動產生的中介資料
│   └── extracted_data.json # 結構化的所有案例 JSON 資料
├── 📂 src/                 # 💻 核心程式碼
│   ├── extractor.py        # 負責解析文字、萃取錯誤的腳本
│   └── html_renderer.py    # 負責讀取 JSON 並呼叫 Playwright 繪製截圖
├── 🐍 main.py              # 🚀 啟動入口 (自動化 Orchestrator)
├── 📄 requirements.txt     # 相依套件清單
└── 📖 README.md            # 本說明文件
```

---

## 🚀 快速上手 (Quick Start)

### 1. 環境安裝
請確保您的電腦已安裝 Python 3.8 以上版本，然後開啟終端機執行以下指令：

```bash
# 安裝必要的 Python 套件
pip install -r requirements.txt

# 下載 Playwright 所需的 Chromium 無頭瀏覽器
python -m playwright install chromium
```

### 2. 準備測試資料
1. 進入 `input/` 資料夾，複製 `_template` 資料夾並重新命名為 `caseXX`（例如 `case04`）。
2. 在裡面放入您的 Email 檔案（`.md` 或 `.txt`）以及 Log 檔案（`.log`）。

### 3. 一鍵執行
在專案根目錄執行以下指令：

```bash
python main.py
```

### 4. 查看成果
執行完畢後，請到 `output/` 資料夾中查看熱騰騰的 `caseXX_report.png` 截圖！

---

## 🏗️ 系統架構說明 (Architecture)

本專案採用 **Pipeline Pattern (管線模式)**，由 `main.py` 依序調度兩個獨立模組：

1. **`src/extractor.py`**
   - **職責**：將所有 `input/` 內的生肉資料（Raw Data）進行清理與正規化匹配。
   - **產出**：集中輸出為 `processed/extracted_data.json`。
2. **`src/html_renderer.py`**
   - **職責**：單純讀取 JSON 中介檔，將資料注入 HTML 模板，並透過 Playwright 的 `networkidle` 狀態確保字體載入完美後，針對 `#capture-area` 進行透明背景截圖。
   - **產出**：平鋪輸出至 `output/` 目錄中。
