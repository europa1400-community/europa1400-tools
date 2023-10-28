import pickle
from pathlib import Path

import numpy as np

from europa1400_tools.cli.common_options import CommonOptions
from europa1400_tools.const import BAF_EXTENSION, JSON_EXTENSION, OUTPUT_META_DIR
from europa1400_tools.construct.baf import Baf, Vector3
from europa1400_tools.models.metadata import AnimationMetadata
from europa1400_tools.rich.progress import Progress


class AnimationsPreprocessor:
    def preprocess_animations(
        self,
        animation_pickle_paths: list[Path],
    ) -> list[AnimationMetadata]:
        """Preprocess animations."""

        progress = Progress(
            title="Preprocessing animations",
            total_file_count=len(animation_pickle_paths),
        )

        animation_metadatas: list[AnimationMetadata] = []

        with progress:
            for animation_pickle_path in animation_pickle_paths:
                relative_path = animation_pickle_path.relative_to(
                    CommonOptions.instance.decoded_animations_path
                )

                progress.file_path = relative_path

                animation_metadata_path = (
                    CommonOptions.instance.converted_animations_path
                    / OUTPUT_META_DIR
                    / relative_path
                ).with_suffix(JSON_EXTENSION)

                if not animation_metadata_path.parent.exists():
                    animation_metadata_path.parent.mkdir(parents=True)

                if (
                    animation_metadata_path.exists()
                    and CommonOptions.instance.use_cache
                ):
                    animation_metadata = AnimationMetadata.from_json(
                        animation_metadata_path.read_text()
                    )
                    animation_metadatas.append(animation_metadata)
                    progress.cached_file_count += 1
                    continue

                with open(animation_pickle_path, "rb") as file:
                    baf: Baf = pickle.load(file)

                vertices_per_key = baf.get_vertices_per_key()

                animation_metadata = AnimationMetadata(
                    name=baf.path.stem,
                    path=relative_path.with_suffix(BAF_EXTENSION),
                    vertices_count=vertices_per_key.shape[1],
                )

                animation_metadatas.append(animation_metadata)
                animation_metadata_path.write_text(animation_metadata.to_json(indent=4))

                progress.completed_file_count += 1

        return animation_metadatas

    @staticmethod
    def map_animation(baf: Baf, bgf_to_vertices: dict[Path, np.ndarray]) -> list[Path]:
        """Map animation to object."""

        mapped_bgfs: list[Path] = []
        baf_vertices: list[Vector3] = []

        for model in baf.body.keys[0].models:
            baf_vertices.extend(model.vertices)

        baf_vertices_np = np.array(
            [[vertex.x, vertex.y, vertex.z] for vertex in baf_vertices],
            dtype=np.float32,
        )

        if baf.path.stem.lower() == "sitzung1_kutte":
            pass

        for bgf_path, bgf_vertices_np in bgf_to_vertices.items():
            if bgf_vertices_np.shape[0] != baf_vertices_np.shape[0]:
                continue

            baf_name = baf.path.stem
            bgf_name = bgf_path.stem

            baf_name_parts = [part.lower() for part in baf_name.split("_")]
            bgf_name_parts = [part.lower() for part in bgf_name.split("_")]

            baf_name_parts = [
                "".join([char for char in part]) for part in baf_name_parts
            ]
            bgf_name_parts = [
                "".join([char for char in part]) for part in bgf_name_parts
            ]

            if not any(
                baf_name_part in bgf_name_parts for baf_name_part in baf_name_parts
            ):
                continue

            mapped_bgfs.append(bgf_path)

        return mapped_bgfs
