import pickle

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.construct.base_construct import BaseConstruct
from europa1400_tools.extractor.file_extractor import FileExtractor
from europa1400_tools.models.gilde_file import GildeArchive, GildeAsset, GildeFile
from europa1400_tools.rich.progress import Progress


class FileDecoder:
    """Decode files."""

    def decode_files(self, files: list[GildeFile]) -> list[GildeAsset]:
        assets_to_extract: list[GildeAsset] = []
        assets: list[GildeAsset] = []

        extractor = FileExtractor()

        for file in files:
            if isinstance(file, GildeArchive):
                extracted_assets = extractor.extract([file])
                assets.extend(
                    filter(
                        lambda asset: asset.source_format.construct_type is not None,
                        extracted_assets,
                    )
                )
                continue

            assets.append(file)

        assets_to_extract = list(
            filter(
                lambda asset: asset.source_path.is_archive
                and not asset.extracted_path.exists(),
                assets,
            )
        )

        if len(assets_to_extract) > 0:
            extractor.extract(assets_to_extract)

        progress = Progress(
            title=f"Decoding assets",
            total_file_count=len(assets),
        )

        decoded_assets: list[GildeAsset] = []

        with progress:
            for asset in assets:
                progress.file_path = asset.path

                if asset.decoded_path.exists() and CommonOptions.instance.use_cache:
                    decoded_assets.append(asset)
                    progress.cached_file_count += 1
                    continue

                asset.decoded_path.parent.mkdir(parents=True, exist_ok=True)

                decoded_value = self.decode_asset(asset)
                decoded_value.path = asset.path

                with open(asset.decoded_path, "wb") as decoded_output_file:
                    pickle.dump(
                        decoded_value,
                        decoded_output_file,
                    )

                decoded_assets.append(asset)
                progress.completed_file_count += 1

        return decoded_assets

    def decode_asset(self, asset: GildeAsset) -> BaseConstruct:
        """Decode file."""

        return asset.source_format.construct_type.from_file(asset.extracted_path)

    # def decode_assets(self, assets: list[GildeAsset] | None = None) -> list[GildeAsset]:
    #     """Decode files."""

    #     file_extractor = FileExtractor()

    #     if assets is None:
    #         if self.is_archive and self.extracted_path is not None:
    #             extracted_file_paths = file_extractor.extract(
    #                 self.game_path, self.extracted_path, self.file_suffix
    #             )
    #         elif self.is_single_file:
    #             extracted_file_paths = [self.game_path]
    #         else:
    #             extracted_file_paths = get_files(self.game_path, self.file_suffix)
    #     elif self.extracted_path is not None:
    #         extractable_file_paths = [
    #             file_path.resolve().relative_to(self.extracted_path)
    #             if file_path.resolve().is_relative_to(self.extracted_path)
    #             else file_path
    #             for file_path in assets
    #             if normalize(file_path.suffix) == self.file_suffix
    #         ]
    #         extracted_game_file_paths = file_extractor.extract_files(
    #             extractable_file_paths,
    #             self.game_path,
    #             self.extracted_path,
    #             self.file_suffix,
    #         )
    #         extracted_file_paths.extend(extracted_game_file_paths)

    #     if len(extracted_file_paths) == 0:
    #         return []

    #     progress = Progress(
    #         title=f"Decoding {self.construct_type.__name__}",
    #         total_file_count=len(extracted_file_paths),
    #     )

    #     with progress:
    #         for extracted_file_path in extracted_file_paths:
    #             if normalize(extracted_file_path.suffix) != normalize(self.file_suffix):
    #                 continue

    #             relative_path: Path = extracted_file_path

    #             if (
    #                 self.extracted_path is not None
    #                 and extracted_file_path.is_relative_to(self.extracted_path)
    #             ):
    #                 relative_path = extracted_file_path.relative_to(self.extracted_path)

    #             progress.file_path = relative_path.as_posix()

    #             decoded_output_path = (
    #                 self.decoded_path
    #                 if self.is_single_file
    #                 else (self.decoded_path / extracted_file_path).with_suffix(
    #                     PICKLE_EXTENSION
    #                 )
    #             )

    #             if decoded_output_path.exists() and CommonOptions.instance.use_cache:
    #                 decoded_file_paths.append(decoded_output_path)
    #                 progress.cached_file_count += 1
    #                 continue

    #             decoded_value = self.decode_asset(extracted_file_path)
    #             decoded_value.path = relative_path

    #             if not decoded_output_path.parent.exists():
    #                 decoded_output_path.parent.mkdir(parents=True)

    #             with open(decoded_output_path, "wb") as decoded_output_file:
    #                 pickle.dump(
    #                     decoded_value,
    #                     decoded_output_file,
    #                 )

    #             decoded_file_paths.append(decoded_output_path)

    #             progress.completed_file_count += 1

    #     return decoded_file_paths
