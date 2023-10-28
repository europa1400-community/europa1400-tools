from pathlib import Path
from typing import Any

from rich.console import Group
from rich.live import Live, RenderableType
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn
from rich.progress import Progress as RichProgress
from rich.progress import TimeRemainingColumn


class Progress:
    title: str
    panel_title: str
    _total_file_count: int
    _cached_file_count: int
    _file_path: str
    _completed_file_count: int
    progress: RichProgress
    live: Live

    def __init__(self, title: str, total_file_count: int):
        self.title = title
        self._total_file_count = total_file_count
        self._completed_file_count = 0
        self._cached_file_count = 0
        self._file_path = ""
        self.panel_title = title

        self.progress = RichProgress(
            TimeRemainingColumn(elapsed_when_finished=True),
            BarColumn(),
            MofNCompleteColumn(),
        )
        self.progress.add_task(title, total=total_file_count)
        self.live = Live(self.panel, refresh_per_second=10)

    @property
    def panel(self) -> Panel:
        return Panel(
            Group(
                self.progress,
                f"Used cache for {self.cached_file_count}/{self.total_file_count}"
                + " files :floppy_disk:",
            ),
            title=self.panel_title,
            title_align="left",
        )

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, value: str) -> None:
        self._file_path = value
        self.panel_title = f"{self.title}: {value}"
        self.refresh()

    @property
    def total_file_count(self) -> int:
        return self._total_file_count

    @total_file_count.setter
    def total_file_count(self, value: int) -> None:
        self._total_file_count = value
        self.refresh()

    @property
    def cached_file_count(self) -> int:
        return self._cached_file_count

    @cached_file_count.setter
    def cached_file_count(self, value: int) -> None:
        previous_value = self._cached_file_count

        if value < previous_value:
            raise ValueError("Cached file count can only be increased.")

        self._cached_file_count = value
        self.refresh()

    @property
    def completed_file_count(self) -> int:
        return self._completed_file_count

    @completed_file_count.setter
    def completed_file_count(self, value: int) -> None:
        previous_value = self._completed_file_count

        if value < previous_value:
            raise ValueError("Completed file count can only be increased.")

        self._completed_file_count = value
        self.refresh()

    def __enter__(self) -> "Progress":
        self.live.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.live.__exit__(exc_type, exc_value, traceback)

    def refresh(self) -> None:
        self.progress.update(
            self.progress.task_ids[0],
            completed=self.completed_file_count + self.cached_file_count,
            total=self.total_file_count,
        )
        self.live.update(self.panel)
