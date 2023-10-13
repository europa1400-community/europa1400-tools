import shutil
from pathlib import Path

from europa_1400_tools.const import MTL_EXTENSION, OBJ_EXTENSION, TargetFormat
from europa_1400_tools.construct.baf import Vector3
from europa_1400_tools.construct.bgf import Bgf, BgfModel, Face, TextureMapping
from europa_1400_tools.converter.bgf_converter import BgfConverter
from europa_1400_tools.converter.common import Texture


class BgfWavefrontConverter(BgfConverter):
    """Class for converting BGF files to wavefront."""

    def convert_bgf_file(
        self,
        bgf: Bgf,
        output_path: Path,
        target_format: TargetFormat,
        textures: list[Texture],
    ) -> list[Path]:
        obj_output_path = output_path / Path(bgf.name).with_suffix(OBJ_EXTENSION)
        mtl_output_path = output_path / Path(bgf.name).with_suffix(MTL_EXTENSION)

        obj_string: str = ""
        mtl_name = Path(bgf.name).with_suffix(MTL_EXTENSION)
        mtl_string: str = ""

        obj_string += f"mtllib {mtl_name}\n"

        models: list[BgfModel] = [
            game_object.model
            for game_object in bgf.game_objects
            if game_object.model is not None
        ]

        if not models:
            raise ValueError("no models found")

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
            vertices: list[Vector3] = [vertex for vertex in model.vertices]
            faces: list[Face] = [polygon.face for polygon in model.polygons]
            normals: list[Vector3] = [
                polygon.normal
                for polygon in model.polygons
                if polygon.normal is not None
            ]

            materials: list[str] = [
                Path(textures[texture_index].main_texture_name).stem
                for texture_index in texture_indices
                if texture_index < len(bgf.textures)
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

        for texture in textures:
            material_name = Path(texture.main_texture_name).stem

            mtl_string += f"newmtl {material_name}\n"
            mtl_string += "Ka 1.0 1.0 1.0\n"
            mtl_string += "Kd 1.0 1.0 1.0\n"
            mtl_string += "Ks 0.0 0.0 0.0\n"
            mtl_string += f"map_Kd {texture.main_texture_name}\n"

            shutil.copy(texture.main_texture_path, output_path)

        with open(obj_output_path, "w") as obj_file:
            obj_file.write(obj_string)

        with open(mtl_output_path, "w") as mtl_file:
            mtl_file.write(mtl_string)

        return [obj_output_path]
