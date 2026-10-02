import json
import os
import subprocess
import sys

from PyQt6.QtCore import QThread, pyqtSignal


class ParseWorker(QThread):
    """後台解析影片 / 播放列表資訊。"""

    log = pyqtSignal(str)
    finished_ok = pyqtSignal(list)   # list[dict]
    finished_err = pyqtSignal(str)

    def __init__(self, url: str, ytdlp_path: str, cookie_path: str = "", parent=None):
        super().__init__(parent)
        self.url = url
        self.ytdlp_path = ytdlp_path
        self.cookie_path = cookie_path

    def run(self):
        if not os.path.isfile(self.ytdlp_path):
            self.finished_err.emit(f"搵唔到 yt-dlp：{self.ytdlp_path}")
            return

        self.log.emit("[解析] 開始解析（播放列表可能需時 1-2 分鐘，請耐心等候）…")

        args = [
            self.ytdlp_path,
            "--dump-json",
            "--no-warnings",
            "--skip-download",
            "--ignore-errors",
        ]
        if self.cookie_path and os.path.isfile(self.cookie_path):
            args += ["--cookies", self.cookie_path]
        args.append(self.url)

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"

        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=600,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
            )
        except subprocess.TimeoutExpired:
            self.finished_err.emit("解析逾時（10 分鐘）")
            return
        except Exception as e:
            self.finished_err.emit(f"啟動解析失敗：{e}")
            return

        if result.returncode != 0:
            self.finished_err.emit(f"yt-dlp 解析失敗：\n{result.stderr[-500:]}")
            return

        items = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            items.append(self._extract_info(data))

        if not items:
            self.finished_err.emit("解析成功但冇攞到任何資料")
            return

        self.log.emit(f"[解析] 共 {len(items)} 條項目")
        self.finished_ok.emit(items)

    @staticmethod
    def _extract_info(data: dict) -> dict:
        """從 yt-dlp JSON 抽我哋要用嘅欄位。"""
        duration = data.get("duration") or 0
        if duration:
            h = int(duration // 3600)
            m = int((duration % 3600) // 60)
            s = int(duration % 60)
            duration_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        else:
            duration_str = "—"

        formats = []
        for f in data.get("formats", []) or []:
            if f.get("vcodec") and f["vcodec"] != "none":
                formats.append({
                    "format_id": f.get("format_id", ""),
                    "ext": f.get("ext", ""),
                    "resolution": f.get("resolution") or f.get("format_note", ""),
                    "fps": f.get("fps"),
                    "vcodec": f.get("vcodec", ""),
                    "filesize": f.get("filesize") or f.get("filesize_approx"),
                })

        return {
            "id": data.get("id", ""),
            "title": data.get("title", "（無標題）"),
            "url": data.get("webpage_url") or data.get("url", ""),
            "duration": duration_str,
            "duration_sec": duration,
            "uploader": data.get("uploader") or data.get("channel", ""),
            "extractor": data.get("extractor", ""),
            "formats": formats,
            "is_playlist_item": data.get("_type") == "url",
        }