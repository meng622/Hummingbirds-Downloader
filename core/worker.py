from PyQt6.QtCore import QThread, pyqtSignal

from core.downloader import (
    YtDlpDownloader, LogEvent, ProgressEvent, FinishEvent
)


class DownloadWorker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(float, str, str, str, str)
    finished_ok = pyqtSignal(str)
    finished_err = pyqtSignal(str)

    def __init__(self, url: str, options: dict, parent=None):
        super().__init__(parent)
        self.url = url
        self.options = options
        self.downloader = YtDlpDownloader()
        self._cancelled = False
        self._paused = False
        self._process_pid: int | None = None

    def run(self):
        try:
            self.downloader.on_process_start = self._on_process_start
            for event in self.downloader.download(self.url, self.options):
                if self._cancelled:
                    break
                if self._paused:
                    while self._paused and not self._cancelled:
                        self.msleep(200)

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

    def _on_process_start(self, pid: int):
        self._process_pid = pid

    def pause(self):
        self._paused = True
        self._suspend_process()

    def resume(self):
        self._paused = False
        self._resume_process()

    def is_paused(self) -> bool:
        return self._paused

    def cancel(self):
        self._cancelled = True
        self._paused = False
        self.downloader.cancel()

    def _suspend_process(self):
        if self._process_pid is None:
            return
        try:
            import psutil
            p = psutil.Process(self._process_pid)
            p.suspend()
        except Exception:
            pass

    def _resume_process(self):
        if self._process_pid is None:
            return
        try:
            import psutil
            p = psutil.Process(self._process_pid)
            p.resume()
        except Exception:
            pass