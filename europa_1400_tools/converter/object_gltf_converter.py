from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pygltflib import (
    ANIM_LINEAR,
    ARRAY_BUFFER,
    ELEMENT_ARRAY_BUFFER,
    FLOAT,
    GLTF2,
    MASK,
    SCALAR,
    UNSIGNED_INT,
    VEC2,
    VEC3,
    WEIGHTS,
    Accessor,
    Animation,
    AnimationChannel,
    AnimationChannelTarget,
    AnimationSampler,
    Attributes,
    Buffer,
    BufferView,
    Image,
    Material,
    Mesh,
    Node,
    PbrMetallicRoughness,
    Primitive,
    Scene,
    Texture,
    TextureInfo,
)

from europa_1400_tools.const import GLTF_EXTENSION
from europa_1400_tools.construct.baf import Baf
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.helpers import (
    bitmap_to_gltf_uri,
    bytes_to_gltf_uri,
    find_texture_path,
)


@dataclass
class GltfPrimitive:
    """Class representing a primitive in a gLTF file."""

    vertices: np.ndarray
    vertices_per_key: np.ndarray | None
    normals: np.ndarray
    uvs: np.ndarray
    indices: np.ndarray
    texture_index: int


@dataclass
class GltfMesh:
    """Class representing a mesh in a gLTF file."""

    name: str
    primitives: list[GltfPrimitive]


class ObjectGltfConverter(BaseConverter[Bgf, tuple[str, GLTF2]]):
    """Class for converting the object file to gltf."""

    @staticmethod
    def _add_gltf_data(
        gltf: GLTF2,
        data: np.ndarray,
        data_type: int,
        data_format: str,
        name: str = "",
        minmax: bool = True,
        buffer_type: int | None = None,
    ) -> tuple[Buffer, BufferView, Accessor]:
        data_bytes = data.tobytes()

        data_buffer = Buffer(
            byteLength=len(data_bytes),
            uri=bytes_to_gltf_uri(data_bytes),
            extras={
                "name": name,
            },
        )
        gltf.buffers.append(data_buffer)

        data_buffer_view = BufferView(
            buffer=len(gltf.buffers) - 1,
            byteLength=len(data_bytes),
            byteOffset=0,
            target=buffer_type,
            extras={
                "name": name,
            },
        )
        gltf.bufferViews.append(data_buffer_view)

        min: list[float] | None = None
        max: list[float] | None = None

        if minmax:
            if data.ndim == 1:
                min = [float(np.min(data))]
                max = [float(np.max(data))]
            else:
                min = [float(np.min(data[:, i])) for i in range(data.shape[1])]
                max = [float(np.max(data[:, i])) for i in range(data.shape[1])]

        data_accessor = Accessor(
            bufferView=len(gltf.bufferViews) - 1,
            byteOffset=0,
            componentType=data_type,
            count=len(data),
            type=data_format,
            min=min,
            max=max,
            extras={
                "name": name,
            },
        )
        gltf.accessors.append(data_accessor)

        return data_buffer, data_buffer_view, data_accessor

    @staticmethod
    def _convert_mesh(
        value: Bgf, baf: Baf | None, extracted_textures_path: Path, name: str
    ) -> Mesh:
        """Convert Bgf to gltf mesh."""

        gltf_primitives = []
        gltf_mesh = GltfMesh(
            name=name,
            primitives=gltf_primitives,
        )

        texture_indices = set(
            polygon.texture_index for polygon in value.mapping_object.polygons
        )

        bgf_vertices = np.array(
            [
                [
                    vertex_mapping.vertex1.x,
                    vertex_mapping.vertex1.y,
                    vertex_mapping.vertex1.z,
                ]
                for vertex_mapping in value.mapping_object.vertex_mappings
            ],
            dtype=np.float32,
        )

        bgf_normals = np.array(
            [
                [
                    vertex_mapping.vertex2.x,
                    vertex_mapping.vertex2.y,
                    vertex_mapping.vertex2.z,
                ]
                for vertex_mapping in value.mapping_object.vertex_mappings
            ],
            dtype=np.float32,
        )

        bgf_vertices_per_key = None
        if baf is not None:
            bgf_vertices_per_key = baf.get_vertices_per_key()

        for texture_index in texture_indices:
            # skip indices of missing textures
            if texture_index >= len(value.footer.texture_names):
                continue

            indices = []
            vertices = []
            normals = []
            uvs = []

            vertices_per_key = None
            if bgf_vertices_per_key is not None:
                # create a new empty array of the same shape as bgf_vertices_per_key,
                # but the axis=1 will be variable and be appended to
                vertices_per_key = [[] for _ in range(bgf_vertices_per_key.shape[0])]

            polygons = [
                polygon
                for polygon in value.mapping_object.polygons
                if polygon.texture_index == texture_index
            ]
            indices_per_polygon = np.array(
                [
                    [
                        polygon.face.a,
                        polygon.face.b,
                        polygon.face.c,
                    ]
                    for polygon in polygons
                ]
            )
            uvs_per_polygon = np.array(
                [
                    [
                        [
                            polygon.texture_mapping.a.u,
                            polygon.texture_mapping.a.v,
                        ],
                        [
                            polygon.texture_mapping.b.u,
                            polygon.texture_mapping.b.v,
                        ],
                        [
                            polygon.texture_mapping.c.u,
                            polygon.texture_mapping.c.v,
                        ],
                    ]
                    for polygon in polygons
                ]
            )

            vertex_dict = {}

            for face, uvs_per_face in zip(indices_per_polygon, uvs_per_polygon):
                for vertex_index, uv in zip(face, uvs_per_face):
                    key = (vertex_index, uv[0], uv[1])
                    if key not in vertex_dict:
                        vertex_dict[key] = len(vertices)
                        vertex = bgf_vertices[vertex_index]
                        vertices.append(vertex)
                        normals.append(bgf_normals[vertex_index])
                        uvs.append(uv)

                        if vertices_per_key is not None:
                            for keyframe in range(bgf_vertices_per_key.shape[0]):
                                vertex_per_key = bgf_vertices_per_key[keyframe][
                                    vertex_index
                                ]
                                vertices_per_key[keyframe].append(vertex_per_key)

                    index = vertex_dict[key]
                    indices.append(index)

            indices = np.array(indices, dtype=np.uint32)
            vertices = np.array(vertices, dtype=np.float32)
            normals = np.array(normals, dtype=np.float32)
            uvs = np.array(uvs, dtype=np.float32)

            if vertices_per_key is not None:
                vertices_per_key = np.array(vertices_per_key, dtype=np.float32)

            if np.isnan(uvs).any():
                uvs = np.nan_to_num(uvs)

            if vertices_per_key is not None and np.isnan(vertices_per_key).any():
                raise ValueError("vertices_per_key contains nan")

            gltf_primitive = GltfPrimitive(
                indices=indices,
                vertices=vertices,
                vertices_per_key=vertices_per_key,
                normals=normals,
                uvs=uvs,
                texture_index=texture_index,
            )
            gltf_primitives.append(gltf_primitive)

        return gltf_mesh

    @staticmethod
    def convert(value: Bgf, **kwargs) -> tuple[str, GLTF2]:
        """Convert Bgf to gltf."""

        baf: Baf | None = kwargs.get("baf", None)
        extracted_textures_path: Path | None = kwargs.get(
            "extracted_textures_path", None
        )

        if extracted_textures_path is None:
            raise ValueError("extracted_textures_path is required")

        name: str | None = kwargs.get("name", None)

        if name is None:
            raise ValueError("name is required")

        gltf = GLTF2()

        gltf_mesh = ObjectGltfConverter._convert_mesh(
            value, baf, extracted_textures_path, name
        )

        scene = Scene(nodes=[0])
        gltf.scenes.append(scene)

        primitives: list[Primitive] = []
        mesh = Mesh(
            primitives=primitives,
        )
        gltf.meshes.append(mesh)

        node = Node(
            mesh=0,
        )
        gltf.nodes.append(node)

        for i, gltf_primitive in enumerate(gltf_mesh.primitives):
            primitive = Primitive(
                attributes={
                    "POSITION": len(gltf.accessors) + 1,
                    "NORMAL": len(gltf.accessors) + 2,
                    "TEXCOORD_0": len(gltf.accessors) + 3,
                },
                indices=len(gltf.accessors),
                material=gltf_primitive.texture_index,
            )
            primitives.append(primitive)

            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.indices,
                buffer_type=ELEMENT_ARRAY_BUFFER,
                data_type=UNSIGNED_INT,
                data_format=SCALAR,
                name=f"indices_{i}",
                minmax=False,
            )

            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.vertices,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC3,
                name=f"vertices_{i}",
            )

            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.normals,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC3,
                name=f"vertex_normals_{i}",
            )

            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.uvs,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC2,
                name=f"uv_coordinates_{i}",
            )

            if gltf_primitive.vertices_per_key is not None:
                for j, anim_vertices in enumerate(gltf_primitive.vertices_per_key):
                    relative_anim_vertices = anim_vertices - gltf_primitive.vertices
                    ObjectGltfConverter._add_gltf_data(
                        gltf=gltf,
                        data=relative_anim_vertices,
                        buffer_type=ARRAY_BUFFER,
                        data_type=FLOAT,
                        data_format=VEC3,
                        name=f"vertices_{i}_{j}",
                    )

                    primitive.targets.append(
                        Attributes(
                            POSITION=len(gltf.accessors) - 1,
                        )
                    )

        texture_names = value.footer.texture_names

        missing_texture_indices: list[int] = []

        for i, texture_name in enumerate(texture_names):
            texture_path = find_texture_path(texture_name, extracted_textures_path)

            if texture_path is None:
                missing_texture_indices.append(i)
                continue

            texture_uri = bitmap_to_gltf_uri(texture_path)

            gltf.images.append(
                Image(
                    uri=texture_uri,
                )
            )
            gltf.textures.append(
                Texture(
                    source=len(gltf.images) - 1,
                )
            )
            gltf.materials.append(
                Material(
                    pbrMetallicRoughness=PbrMetallicRoughness(
                        baseColorTexture=TextureInfo(
                            index=len(gltf.textures) - 1,
                        ),
                        metallicFactor=0.0,
                        roughnessFactor=1.0,
                    ),
                    doubleSided=True,
                    alphaMode=MASK,
                )
            )

        for _ in missing_texture_indices:
            gltf.textures.append(
                Texture(
                    source=0,
                )
            )
            gltf.materials.append(
                Material(
                    pbrMetallicRoughness=PbrMetallicRoughness(
                        baseColorTexture=TextureInfo(
                            index=len(gltf.textures) - 1,
                        ),
                        metallicFactor=0.0,
                        roughnessFactor=1.0,
                    ),
                    doubleSided=True,
                    alphaMode=MASK,
                )
            )

        if baf is not None:
            keyframe_count = baf.keyframe_count

            weight_values = []
            for i in range(keyframe_count):
                weight_values.append([0.0] * keyframe_count)
                weight_values[-1][i] = 1.0

            weight_values_flattened = np.array(
                weight_values, dtype=np.float32
            ).flatten()

            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=weight_values_flattened,
                data_type=FLOAT,
                data_format=SCALAR,
                name="weight_values",
                minmax=False,
            )
            weight_values_id = len(gltf.accessors) - 1

            time_values = np.array(
                baf.baf_ini.key_times,
                dtype=np.float32,
            )
            ObjectGltfConverter._add_gltf_data(
                gltf=gltf,
                data=time_values,
                data_type=FLOAT,
                data_format=SCALAR,
                name="time_values",
            )
            time_values_id = len(gltf.accessors) - 1

            animation = Animation(
                name="animation",
                samplers=[
                    AnimationSampler(
                        input=time_values_id,
                        interpolation=ANIM_LINEAR,
                        output=weight_values_id,
                    ),
                ],
                channels=[
                    AnimationChannel(
                        sampler=0,
                        target=AnimationChannelTarget(
                            node=0,
                            path=WEIGHTS,
                        ),
                    ),
                ],
            )
            gltf.animations.append(animation)

        return gltf

    @staticmethod
    def convert_and_export(value: Bgf, output_path: Path, **kwargs) -> list[Path]:
        """Convert Bgf to gltf and export it to the given output path."""

        if not output_path.exists():
            output_path.mkdir(parents=True)

        extracted_textures_path = kwargs.get("extracted_textures_path", None)

        if extracted_textures_path is None:
            raise ValueError("extracted_textures_path is required")

        path = kwargs.get("path", None)

        if path is None:
            raise ValueError("path is required")

        name = kwargs.get("name", None)

        if name is None:
            raise ValueError("name is required")

        gltf = ObjectGltfConverter.convert(value, **kwargs)

        gltf_output_path = output_path / Path(name).with_suffix(GLTF_EXTENSION)

        gltf.save(gltf_output_path)

        return [gltf_output_path]
