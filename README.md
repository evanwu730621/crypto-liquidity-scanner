# Crypto SMC Liquidity Sweep Scanner

這是一個基於 Python 與 Flask 開發的輕量級量化分析微型服務，專門用來偵測加密貨幣（如 ETH-USD）的 **Smart Money Concept (SMC)** 價格行為：**流動性獵取與反轉 (Liquidity Sweep & Reversal)**。

## 🚀 核心特色
- **自動化流動性比對**：自動抓取 Yahoo Finance 的每日與 1 小時歷史數據，計算前一日高點 (PDH)。
- **反轉訊號偵測**：精準捕捉價格突破前高後迅速收回的「獵取行為」，或挑戰前高受阻的阻力點。
- **輕量化 RESTful API**：結合 Flask 提供即時的 JSON 訊號輸出，並附帶簡潔的 Tailwind CSS互動介面。

## 🛠️ 技術堆疊
- **Language**: Python 3.x
- **Web Framework**: Flask
- **Data Analysis**: Pandas, yfinance
- **UI Styling**: Tailwind CSS

## 💡 如何在本機執行
1. 安裝相依套件：
   ```bash
   pip install -r requirements.txt