# 蜂鳥下載器 Hummingbirds Downloader
### 專為多平台影片下載打造的高效能綜合下載器
### A High-Performance Multi-Platform Video Downloader

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

[繁體中文](#繁體中文) | [English](#english)

---

## 繁體中文

### 簡介

**蜂鳥下載器 (Hummingbirds Downloader)** 是一款基於 **PyQt6** 與 **yt-dlp** 開發的高效能綜合影片下載器。支援 YouTube、Instagram、Facebook、Bilibili、X (Twitter) 等各大平台，並整合 **FFmpeg** 與 **MKVToolNix** 實現字幕與彈幕自動合成。本專案在 **DeepSeek AI** 的協助下完成架構設計、功能開發與除錯優化。

### 核心特色

- 🎬 **多平台支援**：YouTube / Instagram / Facebook / Bilibili / X (Twitter) / 其他 yt-dlp 支援平台
- 🎞️ **分辨率選擇**：4K / 2K / 1080p / 720p / 480p / 360p / 僅音訊 (MP3)
- 💬 **B站彈幕**：XML → ASS → MKVToolNix 合成 MKV 字幕軌
- 📝 **字幕下載 + 自動 mux**：支援繁中 / 簡中 / 英 / 日，自動合成 MKV
- 🍪 **Cookie 匯入**：解鎖 IG / FB / B站高畫質，繞過 YouTube 風控
- 📋 **解析預覽**：支援單條影片 + 播放列表，可勾選下載
- 🔄 **多任務佇列**：順序執行，支援暫停 / 繼續 / 刪除 / 全部取消
- 🎨 **三種主題**：跟隨系統 / 淺色 / 深色
- 📦 **完全 Portable**：所有緩存、config 都喺 exe 同層，唔寫 C 盤

### 安裝與使用

#### 1. 下載程式

從 [Releases](https://github.com/meng622/video-downloader/releases) 下載最新版本。

#### 2. 下載外部工具

將以下檔案放入程式資料夾：

| 工具 | 下載連結 |
|---|---|
| `yt-dlp.exe` | https://github.com/yt-dlp/yt-dlp |
| `ffmpeg.exe` / `ffprobe.exe` | https://www.gyan.dev/ffmpeg/builds/ |
| `mkvmerge.exe` | https://mkvtoolnix.download/downloads.html#windows |

#### 3. 使用

1. 貼上影片網址
2. 揀分辨率、字幕
3. 撳「開始下載」

詳細說明請參考下方「使用說明」。

### 使用說明

#### 基本下載

1. 貼上影片網址
2. 揀分辨率、字幕
3. 撳「開始下載」

#### 下載播放列表

1. 貼上播放列表網址
2. 撳「解析」
3. 喺彈出嘅對話框勾選要下載嘅片
4. 撳「開始下載」或「加入佇列」

#### B站彈幕

1. 貼上 B站影片網址
2. 勾「下載彈幕 (Bilibili)」
3. 勾「合成彈幕/字幕」
4. 撳「開始下載」

#### YouTube 字幕

1. 貼上 YouTube 網址
2. 字幕揀「繁體中文」（或想要嘅語言）
3. 勾「合成彈幕/字幕」
4. 撳「開始下載」

#### Cookie 匯入（IG / FB / B站高畫質）

1. 用瀏覽器擴充套件（例如 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)）匯出 `cookies.txt`
2. 撳「匯入…」
3. 揀 `cookies.txt`
4. 之後下載會自動用 cookies

#### 主題切換

狀態欄右下角有下拉選單：跟隨系統 / 淺色 / 深色

### 特別致謝

- 本專案基於 **yt-dlp** 與 **PyQt6** 開發。
- 特別感謝 **DeepSeek AI** 在架構設計、Bug 定位與邏輯優化上的全力協助。

### 許可證

本專案採用 [MIT License](LICENSE) 開源許可證。

---

## English

### Overview

**Hummingbirds Downloader** is a high-performance, multi-platform video downloader built with **PyQt6** and **yt-dlp**. It supports YouTube, Instagram, Facebook, Bilibili, X (Twitter), and other major platforms, with integrated **FFmpeg** and **MKVToolNix** for automatic subtitle and danmaku merging. Architecture design, feature development, and debugging were completed with the assistance of **DeepSeek AI**.

### Key Features

- 🎬 **Multi-Platform Support**: YouTube / Instagram / Facebook / Bilibili / X (Twitter) / other yt-dlp supported platforms
- 🎞️ **Resolution Selection**: 4K / 2K / 1080p / 720p / 480p / 360p / Audio Only (MP3)
- 💬 **Bilibili Danmaku**: XML → ASS → MKVToolNix merge into MKV subtitle track
- 📝 **Subtitle Download + Auto Mux**: Supports Traditional Chinese / Simplified Chinese / English / Japanese
- 🍪 **Cookie Import**: Unlock IG / FB / Bilibili high-quality, bypass YouTube bot detection
- 📋 **Parse Preview**: Supports single video + playlist, with checkbox selection
- 🔄 **Multi-Task Queue**: Sequential execution with pause / resume / delete / cancel all
- 🎨 **Three Themes**: Follow System / Light / Dark
- 📦 **Fully Portable**: All cache and config stored alongside the exe, no C: drive writes

### Installation

#### 1. Download

Download the latest version from [Releases](https://github.com/meng622/video-downloader/releases).

#### 2. External Tools

Place the following files in the program folder:

| Tool | Download Link |
|---|---|
| `yt-dlp.exe` | https://github.com/yt-dlp/yt-dlp |
| `ffmpeg.exe` / `ffprobe.exe` | https://www.gyan.dev/ffmpeg/builds/ |
| `mkvmerge.exe` | https://mkvtoolnix.download/downloads.html#windows |

### Acknowledgments

- Built on **yt-dlp** and **PyQt6**.
- Special thanks to **DeepSeek AI** for architecture design, bug localization, and logic optimization.

### License

This project is licensed under the [MIT License](LICENSE).
