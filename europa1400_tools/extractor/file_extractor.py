from pathlib import Path
from zipfile import ZipFile, ZipInfo

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.models.gilde_file import (
    GildeArchive,
    GildeAsset,
    GildeDirectory,
    GildeFile,
)
from europa1400_tools.models.gilde_path import GildePath
from europa1400_tools.rich.progress import Progress


class FileExtractor:
    def extract(
        self,
        gilde_files: list[GildeFile],
    ) -> list[GildeAsset]:
        archives: list[GildeArchive] = list(
            filter(lambda gilde_file: isinstance(gilde_file, GildeArchive), gilde_files)
        )
        assets: list[GildeAsset] = list(
            filter(lambda gilde_file: isinstance(gilde_file, GildeAsset), gilde_files)
        )
        directories: list[GildeDirectory] = list(
            filter(
                lambda gilde_file: isinstance(gilde_file, GildeDirectory), gilde_files
            )
        )
        extracted_assets: list[GildeAsset] = []

        for archive in archives:
            progress = Progress(
                title=f"Extracting {archive.path.name}",
                total_file_count=len(archive.path.contained),
            )
            with progress:
                extracted_assets.extend(archive.extract(progress=progress))

        for directory in directories:
            progress = Progress(
                title=f"Extracting {directory.path.name}",
                total_file_count=len(directory.path.contained),
            )
            with progress:
                extracted_assets.extend(directory.extract(progress=progress))

        if len(assets) > 0:
            progress = Progress(
                title="Extracting assets",
                total_file_count=len(assets),
            )

            with progress:
                for asset in list(set(assets)):
                    asset.extract(progress=progress)
                    extracted_assets.append(asset)

        return extracted_assets
