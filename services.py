import pandas as pd
import yfinance as yf

class LiquidityScannerService:
    @staticmethod
    def fetch_daily_data(ticker="ETH-USDT"):
        """精準抓取 ETH-USDT 最近 5 天的每日 (Daily) 歷史資料"""
        symbol = "ETH-USD" if ticker.upper() in ["ETH-USDT", "ETHUSD"] else ticker
        df = yf.download(symbol, period="5d", interval="1d", progress=False)
        
        # 處理 MultiIndex 欄位名稱
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df

    @staticmethod
    def detect_daily_liquidity_signals(ticker="ETH-USDT", tolerance=5.0):
        """
        嚴格掃描最近五天內的每日資料並按「時間由新到舊」排序：
        1. 有獵取前高反轉 -> 顯示獵取
        2. 接近前高 (5點內) -> 顯示接近
        3. 其他 -> 顯示無訊號
        """
        df = LiquidityScannerService.fetch_daily_data(ticker)
        
        if df.empty or len(df) < 2:
            return []

        signals = []

        # 逐日比對最近 5 天的資料
        for i in range(1, len(df)):
            prev_day = df.iloc[i - 1]
            curr_day = df.iloc[i]
            
            prev_high = float(prev_day['High'])
            curr_high = float(curr_day['High'])
            curr_close = float(curr_day['Close'])
            curr_open = float(curr_day['Open'])
            
            day_str = str(df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else df.index[i])

            # 判斷狀態
            is_sweep_reversal = (curr_high > prev_high) and (curr_close < curr_open)
            is_near_high = (abs(curr_high - prev_high) <= tolerance) and (curr_high <= prev_high)

            if is_sweep_reversal:
                signal_type = "Daily Liquidity Sweep & Reversal (有獵取)"
                desc = f"ETH 突破前日高點({prev_high})後遭遇賣壓收黑，確認發生流動性獵取與反轉。"
            elif is_near_high:
                signal_type = "Daily Near High Resistance (有接近)"
                desc = f"ETH 每日高點距離前日高點({prev_high}) 在 ±{tolerance} 點範圍內，呈現觸及前高未破。"
            else:
                signal_type = "No Signal (無訊號)"
                desc = f"當日高點與前日高點差距較大，未達獵取或接近條件。"

            signals.append({
                "date": day_str,
                "type": signal_type,
                "previous_day_high": round(prev_high, 2),
                "trigger_price": round(curr_high, 2),
                "description": desc
            })

        # 將最近 5 天的結果反轉（[::-1]），讓最新日期排在最上方
        return signals[-5:][::-1]