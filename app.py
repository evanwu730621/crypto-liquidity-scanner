from flask import Flask, jsonify, render_template_string
from services import LiquidityScannerService

app = Flask(__name__)

@app.route("/")
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <title>ETH-USDT Daily SMC Scanner</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-white min-h-screen p-6 font-sans">
        <div class="max-w-4xl mx-auto">
            <!-- 標題區塊 -->
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl mb-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 class="text-2xl font-bold text-emerald-400 flex items-center gap-2">
                            <span>📊</span> ETH-USDT Daily SMC Liquidity Scanner
                        </h1>
                        <p class="text-gray-400 text-sm mt-1">專門掃描最近 5 天內，ETH 每日視角下的流動性獵取、接近前高或無訊號狀態。</p>
                    </div>
                    <button onclick="fetchSignals()" id="scan-btn" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2.5 rounded-xl transition shadow-lg flex items-center gap-2 cursor-pointer">
                        <span>載入每日市場訊號</span>
                    </button>
                </div>
            </div>

            <!-- 結果顯示區塊 -->
            <div id="results-container" class="space-y-4">
                <div class="bg-gray-900/50 border border-gray-800/80 rounded-2xl p-12 text-center text-gray-500">
                    點擊上方按鈕開始載入 ETH-USDT 最近 5 天每日流動性分析資料...
                </div>
            </div>
        </div>

        <script>
            async function fetchSignals() {
                const btn = document.getElementById('scan-btn');
                const container = document.getElementById('results-container');
                
                btn.disabled = true;
                btn.innerHTML = `<svg class="animate-spin h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> 分析中...`;
                container.innerHTML = `<div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 text-center text-gray-400 animate-pulse">正在運算最近 5 天價格行為與流動性區間...</div>`;

                try {
                    const response = await fetch('/api/scan');
                    const result = await response.json();

                    if (result.status === 'success') {
                        if (result.signals.length === 0) {
                            container.innerHTML = `<div class="bg-gray-900 border border-gray-800 rounded-2xl p-8 text-center text-gray-400">近期每日資料不足。</div>`;
                        } else {
                            let html = `<div class="text-sm text-gray-400 mb-2">交易對：<span class="text-white font-bold">${result.symbol}</span> (最近 5 天每日視角) | 共顯示 <span class="text-emerald-400 font-bold">${result.total_signals}</span> 筆紀錄</div>`;
                            
                            result.signals.forEach(sig => {
                                const isSweep = sig.type.includes('Sweep');
                                const isNear = sig.type.includes('Near');
                                
                                let badgeColor = 'bg-gray-800 text-gray-400 border-gray-700';
                                if (isSweep) {
                                    badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
                                } else if (isNear) {
                                    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
                                }
                                
                                html += `
                                <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 shadow-md hover:border-gray-700 transition">
                                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
                                        <span class="px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}">
                                            ${sig.type}
                                        </span>
                                        <span class="text-xs text-gray-300 font-mono bg-gray-950 px-2.5 py-1 rounded border border-gray-800">📅 ${sig.date}</span>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4 my-3 text-sm">
                                        <div class="bg-gray-950/50 p-3 rounded-lg border border-gray-800/60">
                                            <span class="text-gray-500 block text-xs">前一日最高價 (PDH)</span>
                                            <span class="text-lg font-bold text-gray-200">${sig.previous_day_high}</span>
                                        </div>
                                        <div class="bg-gray-950/50 p-3 rounded-lg border border-gray-800/60">
                                            <span class="text-gray-500 block text-xs">當日最高價 (Trigger High)</span>
                                            <span class="text-lg font-bold text-emerald-400">${sig.trigger_price}</span>
                                        </div>
                                    </div>
                                    <p class="text-sm text-gray-300 mt-2 bg-gray-950/30 p-3 rounded-lg border border-gray-800/40">
                                        💡 ${sig.description}
                                    </p>
                                </div>`;
                            });
                            container.innerHTML = html;
                        }
                    } else {
                        container.innerHTML = `<div class="bg-rose-950/40 border border-rose-800/50 rounded-2xl p-6 text-rose-300">錯誤：${result.message}</div>`;
                    }
                } catch (err) {
                    container.innerHTML = `<div class="bg-rose-950/40 border border-rose-800/50 rounded-2xl p-6 text-rose-300">網路連線或解析失敗。</div>`;
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = `<span>載入每日市場訊號</span>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/api/scan", methods=["GET"])
def scan_market():
    try:
        signals = LiquidityScannerService.detect_daily_liquidity_signals("ETH-USDT", tolerance=5.0)
        return jsonify({
            "status": "success",
            "symbol": "ETH-USDT",
            "total_signals": len(signals),
            "signals": signals
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)