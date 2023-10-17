from pathlib import Path
from zipfile import ZipFile

from europa_1400_tools.common_options import CommonOptions
from europa_1400_tools.helpers import get_files
from europa_1400_tools.rich import Rich


class FileExtractor:
    common_options: CommonOptions

    def __init__(self, common_options: CommonOptions):
        self.common_options = common_options

    def extract(
        self, file_path: Path, output_path: Path, file_suffix: str | None = None
    ) -> list[Path]:
        """Extract a single file."""

        with ZipFile(file_path, "r") as zip_file:
            zip_file_infos = zip_file.filelist
            zip_file_paths = [
                zip_file_info.filename
                for zip_file_info in zip_file_infos
                if (file_suffix is None or zip_file_info.filename.endswith(file_suffix))
                and not zip_file_info.is_dir()
            ]

            live, progress = Rich.create_live_progress(
                title=f"Extracting {file_path.name}", total=len(zip_file_paths)
            )

            with live:
                if (
                    output_path.exists()
                    and any(output_path.iterdir())
                    and self.common_options.use_cache
                ):
                    file_paths = get_files(output_path, file_suffix=file_suffix)
                    progress.update(
                        progress.task_ids[0],
                        cached_file_count=len(file_paths),
                        completed=len(file_paths),
                    )

                    return file_paths

                if not file_path.exists():
                    raise FileNotFoundError(f"File does not exist: {file_path}")

                if not output_path.exists():
                    output_path.mkdir(parents=True)

                for zip_file_path in zip_file_paths:
                    progress.update(
                        progress.task_ids[0], file_path=zip_file_path, advance=1
                    )
                    zip_file.extract(zip_file_path, output_path)

        file_paths = get_files(output_path, file_suffix=file_suffix)

        return file_paths
