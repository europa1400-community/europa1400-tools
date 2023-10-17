from typing import Any, Iterable

from rich.console import Console, Group
from rich.live import Live, RenderableType
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TimeRemainingColumn,
)
from rich.text import Text


class ProgressPanel(Progress):
    title: str
    panel_title: str
    cached_file_count: int

    def __init__(self, *args, title: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        self.panel_title = title
        self.cached_file_count = 0

    def update(
        self,
        task_id: TaskID,
        *,
        total: float | None = None,
        completed: float | None = None,
        advance: float | None = None,
        description: str | None = None,
        visible: bool | None = None,
        refresh: bool = False,
        **fields: Any,
    ) -> None:
        file_path = fields.pop("file_path", None)
        cached_file_count = fields.pop("cached_file_count", None)
        cached_file_count_advance = fields.pop("cached_file_count_advance", None)

        if file_path is not None:
            self.panel_title = f"{self.title}: {file_path}"

        if cached_file_count is not None:
            self.cached_file_count = cached_file_count

        if cached_file_count_advance is not None:
            self.cached_file_count += cached_file_count_advance

        return super().update(
            task_id,
            total=total,
            completed=completed,
            advance=advance,
            description=description,
            visible=visible,
            refresh=refresh,
            **fields,
        )

    def get_renderables(self) -> Iterable[RenderableType]:
        if hasattr(self, "panel_title"):
            panel_title = self.panel_title
        else:
            panel_title = ""

        if hasattr(self, "cached_file_count"):
            cached_file_count = self.cached_file_count
        else:
            cached_file_count = 0

        if len(self.tasks) > 0:
            total = self.tasks[0].total
        else:
            total = 0

        yield Panel(
            Group(
                self.make_tasks_table(self.tasks),
                Text(f"Used cache for {cached_file_count}/{total} files."),
            ),
            title=panel_title,
            title_align="left",
        )


class Rich:
    @staticmethod
    def create_live_progress(title: str, total: int) -> tuple[Live, ProgressPanel]:
        """Create a live progress."""

        progress = ProgressPanel(
            TimeRemainingColumn(elapsed_when_finished=True),
            BarColumn(),
            MofNCompleteColumn(),
            title=title,
        )
        task = progress.add_task(title, total=total)
        progress.update(task)

        live = Live(progress)

        return live, progress
