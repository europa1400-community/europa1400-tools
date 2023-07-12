import shutil
from pathlib import Path

from europa_1400_tools.const import MTL_EXTENSION, OBJ_EXTENSION
from europa_1400_tools.construct.baf import Vertex
from europa_1400_tools.construct.bgf import Bgf, BgfModel, Face, TextureMapping
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.logger import logger


class ObjectWavefrontConverter(BaseConverter[Bgf, tuple[str, tuple[str, str]]]):
    """Class for converting the object file to wavefront."""

    @staticmethod
    def convert(value: Bgf, **kwargs) -> tuple[str, tuple[str, str]]:
        """Convert Bgf to wavefront."""

        path = kwargs.get("path", None)

        if path is None:
            raise ValueError("path is required")

        name: str = path.stem
        obj_string: str = ""
        mtl_name = Path(name).with_suffix(MTL_EXTENSION)
        mtl_string: str = ""

        obj_string += f"mtllib {mtl_name}\n"

        models: list[BgfModel] = [
            game_object.model
            for game_object in value.game_objects
            if game_object.model is not None
        ]

        if not models:
            raise ValueError("no models found")

        texture_names = [texture.name for texture in value.textures]

        material_names = [texture_name.split(".")[0] for texture_name in texture_names]

        face_offset = 0
        tex_offset = 0

        for i, model in enumerate(models):
            texture_mappings: list[TextureMapping] = [
                polygon.texture_mapping for polygon in model.polygons
            ]
            texture_indices: list[int] = [
                polygon.texture_index
                for polygon in model.polygons
                if polygon.texture_index is not None
            ]
            vertices: list[Vertex] = [vertex for vertex in model.vertices]
            faces: list[Face] = [polygon.face for polygon in model.polygons]
            normals: list[Vertex] = [polygon.normal for polygon in model.polygons]

            materials: list[str] = [
                value.textures[texture_index].name.split(".")[0]
                for texture_index in texture_indices
                if texture_index < len(value.textures)
            ]

            obj_string += f"o group{i}\n"

            for vertex in vertices:
                obj_string += f"v {vertex.x} {vertex.z} {-vertex.y}\n"

            for normal in normals:
                obj_string += f"vn {normal.x} {normal.z} {-normal.y}\n"

            for texture_mapping in texture_mappings:
                obj_string += f"vt {texture_mapping.a.u} {texture_mapping.a.v} 0\n"
                obj_string += f"vt {texture_mapping.b.u} {texture_mapping.b.v} 0\n"
                obj_string += f"vt {texture_mapping.c.u} {texture_mapping.c.v} 0\n"

            for face_index, (face, material) in enumerate(zip(faces, materials)):
                obj_string += f"usemtl {material}\n"
                obj_string += (
                    f"f {face.a + 1 + face_offset}/"
                    + f"{face_index * 3 + 1 + tex_offset}/{face_index + 1} "
                    + f"{face.b + 1 + face_offset}/"
                    + f"{face_index * 3 + 2 + tex_offset}/{face_index + 1} "
                    + f"{face.c + 1 + face_offset}/"
                    + f"{face_index * 3 + 3 + tex_offset}/{face_index + 1}\n"
                )
            face_offset += len(vertices)
            tex_offset += len(texture_mappings * 3)

        for texture_name, material_name in zip(texture_names, material_names):
            mtl_string += f"newmtl {material_name}\n"
            mtl_string += "Ka 1.0 1.0 1.0\n"
            mtl_string += "Kd 1.0 1.0 1.0\n"
            mtl_string += "Ks 0.0 0.0 0.0\n"
            mtl_string += f"map_Kd {texture_name}\n"

        return name, (obj_string, mtl_string)

    @staticmethod
    def convert_and_export(value: Bgf, output_path: Path, **kwargs) -> list[Path]:
        """Convert Bgf to wavefront."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        extracted_textures_path = kwargs.get("extracted_textures_path", None)

        if extracted_textures_path is None:
            raise ValueError("extracted_textures_path is required")

        name, (obj_string, mtl_string) = ObjectWavefrontConverter.convert(
            value, **kwargs
        )

        obj_output_path = output_path / Path(name).with_suffix(OBJ_EXTENSION)
        mtl_output_path = output_path / Path(name).with_suffix(MTL_EXTENSION)

        with open(obj_output_path, "w") as obj_file:
            obj_file.write(obj_string)

        with open(mtl_output_path, "w") as mtl_file:
            mtl_file.write(mtl_string)

        def either(c):
            return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c

        texture_names = [
            "".join(map(either, texture.name)) for texture in value.textures
        ]

        texture_files_nested = [
            list(extracted_textures_path.rglob(texture_name))
            for texture_name in texture_names
        ]
        texture_files = [item for sublist in texture_files_nested for item in sublist]

        if len(texture_files) != len(texture_names):
            logger.warning(
                "Amount of texture files found differs "
                "from amount specified specified in bgf file."
            )

        for texture_file in texture_files:
            shutil.copy(texture_file, output_path)

        return [obj_output_path]
