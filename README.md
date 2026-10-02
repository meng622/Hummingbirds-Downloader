# 綜合下載器

PyQt6 + yt-dlp 嘅綜合影片下載器，支援多平台、彈幕、字幕、多任務。

---

## 功能

- **多平台下載**：YouTube / Instagram / Facebook / Bilibili / X (Twitter) / 其他 yt-dlp 支援嘅平台
- **分辨率選擇**：4K / 2K / 1080p / 720p / 480p / 360p / 僅音訊 (MP3)
- **字幕下載**：自動 / 繁體中文 / 簡體中文 / 英文 / 日文
- **字幕自動 mux**：YouTube 字幕自動合成 MKV 字幕軌
- **Cookie 匯入**：解鎖 IG、FB、B站高畫質，繞過 YouTube 風控
- **B站彈幕**：下載 XML → 轉 ASS → 用 MKVToolNix 合成 MKV
- **解析預覽**：支援單條影片 + 播放列表，可以勾選邊幾條下載
- **多任務佇列**：順序執行，支援暫停 / 繼續 / 刪除 / 全部取消
- **三種主題**：跟隨系統 / 淺色 / 深色
- **完全 Portable**：所有緩存、暫存、config 都喺 exe 同層，唔寫 C 盤

---

## 依賴

### Python 套件

```bash
pip install PyQt6 psutil requests biliass pyinstaller