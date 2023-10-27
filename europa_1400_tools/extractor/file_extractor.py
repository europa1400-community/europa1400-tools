from pathlib import Path
from zipfile import ZipFile

from europa_1400_tools.cli.common_options import CommonOptions
from europa_1400_tools.helpers import get_files, normalize
from europa_1400_tools.rich.progress import Progress


class FileExtractor:
    def extract_files(
        self,
        file_paths: list[Path],
        archive_path: Path,
        output_path: Path,
        file_suffix: str | None = None,
    ) -> list[Path]:
        """Extract files from archive."""

        extracted_file_paths: list[Path] = []
        extractable_file_paths: list[Path] = []

        progress = Progress(
            title=f"Searching {archive_path.name}",
            total_file_count=len(file_paths),
        )

        with progress:
            with ZipFile(archive_path, "r") as zip_file:
                zip_file_infos = zip_file.filelist

            zip_file_paths: list[Path] = [
                Path(zip_file_info.filename)
                for zip_file_info in zip_file_infos
                if not zip_file_info.is_dir()
                and (
                    file_suffix is None
                    or normalize(Path(zip_file_info.filename).suffix)
                    == normalize(file_suffix)
                )
            ]

            for file_path in file_paths:
                progress.file_path = file_path

                if file_path not in zip_file_paths:
                    progress.completed_file_count += 1
                    continue

                extractable_file_paths.append(file_path)

                progress.completed_file_count += 1

        progress = Progress(
            title=f"Extracting {archive_path.name}",
            total_file_count=len(extractable_file_paths),
        )

        if len(extractable_file_paths) == 0:
            return []

        if not output_path.exists():
            output_path.mkdir(parents=True)

        with progress:
            with ZipFile(archive_path, "r") as zip_file:
                for extractable_file_path in extractable_file_paths:
                    progress.file_path = extractable_file_path

                    if (
                        extractable_file_path.exists()
                        or (output_path / extractable_file_path).exists()
                    ):
                        extracted_file_paths.append(extractable_file_path)
                        progress.cached_file_count += 1
                        continue

                    zip_file_path = next(
                        (
                            zip_file_path.as_posix()
                            for zip_file_path in zip_file_paths
                            if normalize(zip_file_path.name)
                            == normalize(extractable_file_path)
                        ),
                        None,
                    )

                    zip_file.extract(zip_file_path, output_path)

                    extracted_file_paths.append(output_path / extractable_file_path)

                    progress.completed_file_count += 1

        return extracted_file_paths

    def contains(self, file_path: Path, archive_path: Path) -> bool:
        """Check if the archive contains a file."""

        with ZipFile(archive_path, "r") as zip_file:
            zip_file_infos = zip_file.filelist

        zip_file_paths: list[Path] = [
            Path(zip_file_info.filename)
            for zip_file_info in zip_file_infos
            if not zip_file_info.is_dir()
        ]

        return file_path in zip_file_paths

    def extract(
        self, file_path: Path, output_path: Path, file_suffix: str | None = None
    ) -> list[Path]:
        """Extract a single file."""

        with ZipFile(file_path, "r") as zip_file:
            zip_file_infos = zip_file.filelist

            zip_file_paths: list[Path] = [
                Path(zip_file_info.filename)
                for zip_file_info in zip_file_infos
                if not zip_file_info.is_dir()
                and (
                    file_suffix is None
                    or normalize(Path(zip_file_info.filename).suffix)
                    == normalize(file_suffix)
                )
            ]

            progress = Progress(
                title=f"Extracting {file_path.name}",
                total_file_count=len(zip_file_paths),
            )

            with progress:
                if (
                    output_path.exists()
                    and any(output_path.iterdir())
                    and CommonOptions.instance.use_cache
                ):
                    file_paths = get_files(output_path, file_suffix=file_suffix)

                    progress.cached_file_count = len(file_paths)

                    return file_paths

                if not file_path.exists():
                    raise FileNotFoundError(f"File does not exist: {file_path}")

                if not output_path.exists():
                    output_path.mkdir(parents=True)

                for zip_file_path in zip_file_paths:
                    progress.file_path = zip_file_path

                    zip_file.extract(zip_file_path.as_posix(), output_path)

                    progress.completed_file_count += 1

        file_paths = get_files(output_path, file_suffix=file_suffix)

        return file_paths
