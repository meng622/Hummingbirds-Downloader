from PyQt6.QtCore import QThread, pyqtSignal

from core.downloader import (
    YtDlpDownloader, LogEvent, ProgressEvent, FinishEvent
)


class DownloadWorker(QThread):
    """將 yt-dlp 下載放喺後台執行，唔阻塞 GUI。"""

    log = pyqtSignal(str)
    progress = pyqtSignal(float, str, str, str, str)  # percent, speed, eta, downloaded, total
    finished_ok = pyqtSignal(str)
    finished_err = pyqtSignal(str)

    def __init__(self, url: str, options: dict, parent=None):
        super().__init__(parent)
        self.url = url
        self.options = options
        self.downloader = YtDlpDownloader()
        self._cancelled = False

    def run(self):
        try:
            for event in self.downloader.download(self.url, self.options):
                if self._cancelled:
                    break

                if isinstance(event, LogEvent):
                    self.log.emit(event.text)
                elif isinstance(event, ProgressEvent):
                    self.progress.emit(
                        event.percent, event.speed, event.eta,
                        event.downloaded, event.total
                    )
                elif isinstance(event, FinishEvent):
                    if event.success:
                        self.finished_ok.emit(event.message)
                    else:
                        self.finished_err.emit(event.message)
        except Exception as e:
            self.finished_err.emit(f"未預期錯誤：{e}")

    def cancel(self):
        self._cancelled = True
        self.downloader.cancel()