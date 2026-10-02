from PyQt6.QtCore import QObject, pyqtSignal

from core.worker import DownloadWorker


class Task:
    STATE_WAITING = "waiting"
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_DONE = "done"
    STATE_FAILED = "failed"
    STATE_CANCELLED = "cancelled"

    def __init__(self, url: str, options: dict):
        self.url = url
        self.options = options
        self.state = self.STATE_WAITING
        self.progress = 0.0
        self.title = url


class TaskQueue(QObject):
    task_added = pyqtSignal(int, object)
    task_updated = pyqtSignal(int, object)
    task_finished = pyqtSignal(int, object, bool)
    task_removed = pyqtSignal(int)
    all_finished = pyqtSignal()
    progress_info = pyqtSignal(float, str, str, str, str)
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks: list[Task] = []
        self.current_index: int = -1
        self.worker: DownloadWorker | None = None
        self._is_running = False

    # ---------- 新增 / 移除 ----------

    def add_task(self, url: str, options: dict):
        task = Task(url, options)
        self.tasks.append(task)
        idx = len(self.tasks) - 1
        self.task_added.emit(idx, task)
        self.log.emit(f"[佇列] 加入任務 #{idx + 1}：{url}")

    def remove_task(self, index: int):
        if index < 0 or index >= len(self.tasks):
            return

        if index == self.current_index and self.worker and self.worker.isRunning():
            self.worker.cancel()

        self.tasks.pop(index)
        self.task_removed.emit(index)

        if index < self.current_index:
            self.current_index -= 1
        elif index == self.current_index:
            self.current_index -= 1

        self.log.emit(f"[佇列] 移除任務 #{index + 1}")

    def clear_all(self):
        self.cancel_current()
        self.tasks.clear()
        self.current_index = -1
        self._is_running = False
        self.log.emit("[佇列] 已清空所有任務")

    def clear_finished(self):
        new_tasks = []
        for task in self.tasks:
            if task.state in (Task.STATE_WAITING, Task.STATE_RUNNING, Task.STATE_PAUSED):
                new_tasks.append(task)
        removed = len(self.tasks) - len(new_tasks)
        self.tasks = new_tasks
        if removed:
            self.log.emit(f"[佇列] 清除 {removed} 條已完成任務")

    # ---------- 控制 ----------

    def start(self):
        if self._is_running:
            return
        self._is_running = True
        self.current_index = -1
        self._run_next()

    def start_all(self):
        for task in self.tasks:
            if task.state in (Task.STATE_CANCELLED, Task.STATE_FAILED):
                task.state = Task.STATE_WAITING
                task.progress = 0.0
        if not self._is_running:
            self.start()
        else:
            self.log.emit("[佇列] 已有任務進行中，稍後會自動執行新任務")

    def cancel_current(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.log.emit("[佇列] 取消當前任務")

    def cancel_all(self):
        self.cancel_current()
        for idx, task in enumerate(self.tasks):
            if task.state in (Task.STATE_WAITING, Task.STATE_PAUSED):
                task.state = Task.STATE_CANCELLED
                self.task_updated.emit(idx, task)
        self._is_running = False

    def pause_task(self, index: int):
        if index == self.current_index and self.worker and self.worker.isRunning():
            self.worker.pause()
            self.tasks[index].state = Task.STATE_PAUSED
            self.task_updated.emit(index, self.tasks[index])
            self.log.emit(f"[佇列] 暫停任務 #{index + 1}")

    def resume_task(self, index: int):
        if index == self.current_index and self.worker and self.worker.isRunning():
            self.worker.resume()
            self.tasks[index].state = Task.STATE_RUNNING
            self.task_updated.emit(index, self.tasks[index])
            self.log.emit(f"[佇列] 繼續任務 #{index + 1}")

    @property
    def is_running(self) -> bool:
        return self._is_running

    # ---------- 內部執行 ----------

    def _run_next(self):
        if not self._is_running:
            return

        self.current_index += 1
        if self.current_index >= len(self.tasks):
            self._is_running = False
            self.current_index = -1
            self.worker = None
            self.log.emit("[佇列] 全部任務完成")
            self.all_finished.emit()
            return

        task = self.tasks[self.current_index]
        if task.state == Task.STATE_CANCELLED:
            self._run_next()
            return

        task.state = Task.STATE_RUNNING
        self.task_updated.emit(self.current_index, task)
        self.log.emit(f"[佇列] 開始任務 #{self.current_index + 1}：{task.url}")

        idx = self.current_index
        self.worker = DownloadWorker(task.url, task.options)
        self.worker.log.connect(self.log.emit)
        self.worker.progress.connect(
            lambda p, s, e, d, t, i=idx: self._on_progress(i, p, s, e, d, t)
        )
        self.worker.finished_ok.connect(
            lambda msg, i=idx: self._on_task_done(i, True, msg)
        )
        self.worker.finished_err.connect(
            lambda msg, i=idx: self._on_task_done(i, False, msg)
        )
        self.worker.start()

    def _on_progress(self, idx: int, percent: float, speed: str, eta: str, downloaded: str, total: str):
        if idx < 0 or idx >= len(self.tasks):
            return
        task = self.tasks[idx]
        task.progress = percent
        self.task_updated.emit(idx, task)
        self.progress_info.emit(percent, speed, eta, downloaded, total)

    def _on_task_done(self, idx: int, success: bool, msg: str):
        if idx < 0 or idx >= len(self.tasks):
            return
        task = self.tasks[idx]
        if task.state == Task.STATE_CANCELLED:
            return
        task.state = Task.STATE_DONE if success else Task.STATE_FAILED
        if success:
            task.progress = 100.0
        self.task_updated.emit(idx, task)
        self.task_finished.emit(idx, task, success)
        self.log.emit(f"[佇列] 任務 #{idx + 1} {'完成' if success else '失敗'}")
        self._run_next()