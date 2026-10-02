import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Generator


# ---------- 事件類型 ----------

@dataclass
class LogEvent:
    text: str


@dataclass
class ProgressEvent:
    percent: float
    speed: str
    eta: str
    downloaded: str
    total: str


@dataclass
class FinishEvent:
    success: bool
    message: str


Event = LogEvent | ProgressEvent | FinishEvent


# ---------- 主下載器 ----------

class YtDlpDownloader:
    """封裝 yt-dlp.exe 嘅調用。"""

    def __init__(self, ytdlp_path: Optional[str] = None):
        if ytdlp_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if sys.platform.startswith("win"):
                ytdlp_path = os.path.join(base, "yt-dlp.exe")
            else:
                ytdlp_path = os.path.join(base, "yt-dlp")
        self.ytdlp_path = ytdlp_path
        self._process: Optional[subprocess.Popen] = None

    # ---------- 檢查 ----------

    def is_available(self) -> bool:
        return os.path.isfile(self.ytdlp_path)

    # ---------- 參數組裝 ----------

    def build_args(self, url: str, options: dict) -> list[str]:
        args = [
            self.ytdlp_path,
            "--newline",
            "--no-color",
            "--progress",
            "--progress-template",
            "PROGRESS|%(progress._percent_str)s|%(progress._speed_str)s|"
            "%(progress._eta_str)s|%(progress.downloaded_bytes)s|"
            "%(progress.total_bytes_estimate)s",
        ]

        # 輸出資料夾
        out_dir = options.get("output_dir") or "./downloads"
        os.makedirs(out_dir, exist_ok=True)
        args += ["-P", out_dir]

        # 檔名：唔要 ID，清走 Emoji
        args += ["-o", "%(title).200B.%(ext)s"]
        args += ["--replace-in-metadata", "title", r"[^\w\s\-\.\(\)\[\]\u4e00-\u9fff]", ""]

        # 強制合併成 MP4
        args += ["--merge-output-format", "mp4"]

        # 分辨率
        res = options.get("resolution", "最佳畫質")
        res_map = {
            "2160p (4K)": "2160",
            "1440p (2K)": "1440",
            "1080p": "1080",
            "720p": "720",
            "480p": "480",
            "360p": "360",
        }
        if res == "僅音訊 (MP3)":
            args += ["-x", "--audio-format", "mp3"]
        elif res in res_map:
            args += ["-S", f"res:{res_map[res]}"]

        # 字幕
        sub = options.get("subtitle", "不下載")
        sub_map = {
            "繁體中文": "zh-Hant",
            "簡體中文": "zh-Hans",
            "英文": "en",
            "日文": "ja",
        }
        if sub == "自動":
            args += ["--write-auto-subs", "--sub-langs", "all", "--convert-subs", "srt"]
        elif sub in sub_map:
            args += ["--write-subs", "--sub-langs", sub_map[sub], "--convert-subs", "srt"]

        # 唔要 info.json
        args += ["--no-write-info-json"]

        args.append(url)
        return args

    # ---------- 執行下載 ----------

    def download(self, url: str, options: dict) -> Generator[Event, None, None]:
        if not self.is_available():
            yield FinishEvent(False, f"搵唔到 yt-dlp：{self.ytdlp_path}")
            return

        args = self.build_args(url, options)
        out_dir = options.get("output_dir") or "./downloads"
        yield LogEvent(f"[CMD] {' '.join(args)}")

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
            )
        except Exception as e:
            yield FinishEvent(False, f"啟動 yt-dlp 失敗：{e}")
            return

        progress_re = re.compile(
            r"PROGRESS\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)"
        )

        assert self._process.stdout is not None
        for line in self._process.stdout:
            line = line.rstrip("\r\n")
            if not line:
                continue

            # 進度行
            m = progress_re.search(line)
            if m:
                percent_str, speed, eta, downloaded, total = m.groups()
                yield ProgressEvent(
                    percent=self._parse_percent(percent_str),
                    speed=speed.strip() or "—",
                    eta=eta.strip() or "—",
                    downloaded=self._fmt_bytes(downloaded.strip()),
                    total=self._fmt_bytes(total.strip()),
                )
                continue

            # 其他輸出
            yield LogEvent(line)

        # 等 yt-dlp 完成
        code = self._process.wait()
        self._process = None

        # 自己掃描輸出資料夾，搵最新檔案（避免 yt-dlp 中文路徑亂碼）
        if code == 0:
            try:
                files = [
                    os.path.join(out_dir, f)
                    for f in os.listdir(out_dir)
                    if os.path.isfile(os.path.join(out_dir, f))
                ]
                if files:
                    latest = max(files, key=os.path.getmtime)
                    yield LogEvent(f"[完成] {latest}")
            except Exception as e:
                yield LogEvent(f"[警告] 掃描輸出資料夾失敗：{e}")

        if code == 0:
            yield FinishEvent(True, "下載完成 ✅")
        else:
            yield FinishEvent(False, f"yt-dlp 結束，返回碼 {code}")

    # ---------- 取消 ----------

    def cancel(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()

    # ---------- 工具 ----------

    @staticmethod
    def _parse_percent(s: str) -> float:
        s = s.strip().replace("%", "")
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def _fmt_bytes(s: str) -> str:
        if not s or s in ("NA", "None"):
            return "—"
        try:
            n = float(s)
        except ValueError:
            return s
        units = ["B", "KiB", "MiB", "GiB", "TiB"]
        i = 0
        while n >= 1024 and i < len(units) - 1:
            n /= 1024
            i += 1
        return f"{n:.2f}{units[i]}"