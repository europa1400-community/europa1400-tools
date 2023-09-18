import pickle
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

from europa_1400_tools.const import (
    GLB_EXTENSION,
    GLTF_EXTENSION,
    PICKLE_EXTENSION,
    TargetFormat,
)
from europa_1400_tools.construct.baf import Baf
from europa_1400_tools.construct.bgf import Bgf
from europa_1400_tools.converter.bgf_converter import BgfConverter
from europa_1400_tools.decoder.commands import decode_animations, decode_objects
from europa_1400_tools.extractor.commands import extract_file
from europa_1400_tools.helpers import bitmap_to_gltf_uri, bytes_to_gltf_uri
from europa_1400_tools.mapper.commands import map_animations


@dataclass
class GltfPrimitive:
    """Class representing a primitive in a gLTF file."""

    vertices: np.ndarray
    baf_to_vertices_per_key: list[np.ndarray]
    normals: np.ndarray
    uvs: np.ndarray
    indices: np.ndarray
    texture_index: int


@dataclass
class GltfMesh:
    """Class representing a mesh in a gLTF file."""

    name: str
    primitives: list[GltfPrimitive]


class BgfGltfConverter(BgfConverter):
    """Class for converting BGF files to gLTF."""

    def __init__(self, common_options):
        super().__init__(common_options)

        if (
            self.common_options.mapped_animations_path.exists()
            and common_options.use_cache
        ):
            with open(self.common_options.mapped_animations_path, "rb") as input_file:
                self.baf_to_bgfs = pickle.load(input_file)
        else:
            self.extracted_objects_paths = extract_file(
                self.common_options.game_objects_path,
                self.common_options.extracted_objects_path,
            )

            self.extracted_animations_paths = extract_file(
                self.common_options.game_animations_path,
                self.common_options.extracted_animations_path,
            )

            self.decoded_objects_paths = decode_objects(
                common_options, self.extracted_objects_paths
            )

            self.decoded_animations_paths = decode_animations(
                common_options, self.extracted_animations_paths
            )

            self.baf_to_bgfs, _ = map_animations(
                self.common_options.extracted_objects_path,
                self.common_options.extracted_animations_path,
                self.decoded_objects_paths,
                self.decoded_animations_paths,
            )

    def convert_bgf_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        bgf = Bgf.from_file(file_path)
        name = bgf.path.stem

        gltf = GLTF2()

        bafs: list[Baf] = []

        if target_format == TargetFormat.GLTF:
            baf_paths = [
                (self.common_options.decoded_animations_path / baf_path).with_suffix(
                    PICKLE_EXTENSION
                )
                for baf_path, bgfs in self.baf_to_bgfs.items()
                if any(bgf_path.stem.lower() == name.lower() for bgf_path in bgfs)
            ]

            for baf_path in baf_paths:
                with open(baf_path, "rb") as input_file:
                    baf = pickle.load(input_file)
                    bafs.append(baf)

        gltf_mesh = self._convert_mesh(bgf, bafs, name)

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

            self._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.indices,
                buffer_type=ELEMENT_ARRAY_BUFFER,
                data_type=UNSIGNED_INT,
                data_format=SCALAR,
                name=f"indices_{i}",
                minmax=False,
            )

            self._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.vertices,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC3,
                name=f"vertices_{i}",
            )

            self._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.normals,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC3,
                name=f"vertex_normals_{i}",
            )

            self._add_gltf_data(
                gltf=gltf,
                data=gltf_primitive.uvs,
                buffer_type=ARRAY_BUFFER,
                data_type=FLOAT,
                data_format=VEC2,
                name=f"uv_coordinates_{i}",
            )

            total_vertices_per_key: np.ndarray = (
                np.concatenate(gltf_primitive.baf_to_vertices_per_key)
                if gltf_primitive.baf_to_vertices_per_key
                else np.array([])
            )

            for j, anim_vertices in enumerate(total_vertices_per_key):
                relative_anim_vertices = anim_vertices - gltf_primitive.vertices
                self._add_gltf_data(
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

        texture_names = bgf.footer.texture_names

        missing_texture_indices: list[int] = []

        for i, texture_name in enumerate(texture_names):
            texture_path: Path | None = None
            for extracted_textures_path in self.extracted_textures_paths:
                if (
                    extracted_textures_path.stem.lower()
                    == Path(texture_name).stem.lower()
                ):
                    texture_path = extracted_textures_path
                    break

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

        target_index = 0

        if len(bafs) > 0:
            total_keyframe_count = len(total_vertices_per_key)

            bafs = bafs[:1]
            for baf in bafs:
                keyframe_count = baf.keyframe_count

                weight_values = []
                for i in range(keyframe_count):
                    weight_values.append([0.0] * total_keyframe_count)
                    weight_values[-1][target_index + i] = 1.0

                weight_values_flattened = np.array(
                    weight_values, dtype=np.float32
                ).flatten()

                self._add_gltf_data(
                    gltf=gltf,
                    data=weight_values_flattened,
                    data_type=FLOAT,
                    data_format=SCALAR,
                    name="weight_values",
                    minmax=False,
                )
                weight_values_id = len(gltf.accessors) - 1

                time_values: np.ndarray = np.arange(0, keyframe_count, dtype=np.float32)
                if baf.baf_ini is not None and baf.baf_ini.key_times is not None:
                    time_values = np.array(
                        baf.baf_ini.key_times,
                        dtype=np.float32,
                    )

                self._add_gltf_data(
                    gltf=gltf,
                    data=time_values,
                    data_type=FLOAT,
                    data_format=SCALAR,
                    name="time_values",
                )
                time_values_id = len(gltf.accessors) - 1

                animation = Animation(
                    name=baf.path.stem.lower(),
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
                continue
                gltf.animations.append(animation)

                target_index += keyframe_count

        gltf_output_path = output_path / Path(name).with_suffix(GLTF_EXTENSION)
        glb_output_path = output_path / Path(name).with_suffix(GLB_EXTENSION)
        print(len(bafs))
        for baf in bafs:
            print(baf.path.stem)

        # gltf.save(gltf_output_path)
        gltf.save_binary(glb_output_path)

        return [glb_output_path]

    def _add_gltf_data(
        self,
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

    def _convert_mesh(self, bgf: Bgf, bafs: list[Baf], name: str) -> Mesh:
        """Convert Bgf to gltf mesh."""

        gltf_primitives = []
        gltf_mesh = GltfMesh(
            name=name,
            primitives=gltf_primitives,
        )

        texture_indices = set(
            polygon.texture_index for polygon in bgf.mapping_object.polygons
        )

        bgf_vertices = np.array(
            [
                [
                    -vertex_mapping.vertex1.x,
                    vertex_mapping.vertex1.y,
                    -vertex_mapping.vertex1.z,
                ]
                for vertex_mapping in bgf.mapping_object.vertex_mappings
            ],
            dtype=np.float32,
        )

        bgf_normals = np.array(
            [
                [
                    -vertex_mapping.vertex2.x,
                    vertex_mapping.vertex2.y,
                    -vertex_mapping.vertex2.z,
                ]
                for vertex_mapping in bgf.mapping_object.vertex_mappings
            ],
            dtype=np.float32,
        )

        baf_to_bgf_vertices_per_key = []
        for baf in bafs:
            bgf_vertices_per_key = baf.get_vertices_per_key()
            baf_to_bgf_vertices_per_key.append(bgf_vertices_per_key)

        # iterate over all textures
        for texture_index in texture_indices:
            # skip indices of missing textures
            if texture_index >= len(bgf.footer.texture_names):
                continue

            # each texture has its own primitive
            # with its own indices, vertices, normals and uvs
            primitive_indices: list = []
            vertices: list = []
            normals: list = []
            uvs: list = []

            # each texture also has its own animation vertices
            vertices_per_key_per_anim = []
            for bgf_vertices_per_key in baf_to_bgf_vertices_per_key:
                vertices_per_key = np.emptylike(bgf_vertices_per_key, dtype=np.float32)
                vertices_per_key_per_anim.append(vertices_per_key)

            # select all indices with the current texture index
            indices_per_polygon = np.array(
                [
                    [
                        polygon.face.c,
                        polygon.face.b,
                        polygon.face.a,
                    ]
                    for polygon in bgf.mapping_object.polygons
                    if polygon.texture_index == texture_index
                ]
            )
            uvs_per_polygon = np.array(
                [
                    [
                        [
                            polygon.texture_mapping.c.u,
                            polygon.texture_mapping.c.v,
                        ],
                        [
                            polygon.texture_mapping.b.u,
                            polygon.texture_mapping.b.v,
                        ],
                        [
                            polygon.texture_mapping.a.u,
                            polygon.texture_mapping.a.v,
                        ],
                    ]
                    for polygon in bgf.mapping_object.polygons
                    if polygon.texture_index == texture_index
                ]
            )

            vertex_dict = {}

            # iterate
            for face, uvs_per_face in zip(indices_per_polygon, uvs_per_polygon):
                for vertex_index, uv in zip(face, uvs_per_face):
                    key = (vertex_index, uv[0], uv[1])

                    if key not in vertex_dict:
                        vertex_dict[key] = len(vertices)
                        vertex = bgf_vertices[vertex_index]
                        vertices.append(vertex)
                        normals.append(bgf_normals[vertex_index])
                        uvs.append(uv)

                        for bgf_vertices_per_key, vertices_per_key in zip(
                            baf_to_bgf_vertices_per_key, vertices_per_key_per_anim
                        ):
                            for keyframe in range(bgf_vertices_per_key.shape[0]):
                                vertex_per_key = bgf_vertices_per_key[keyframe][
                                    vertex_index
                                ]
                                vertices_per_key = np.append(
                                    vertices_per_key, vertex_per_key
                                )

                    index = vertex_dict[key]
                    primitive_indices.append(index)

            primitive_indices = np.array(primitive_indices, dtype=np.uint32)
            vertices = np.array(vertices, dtype=np.float32)
            normals = np.array(normals, dtype=np.float32)
            uvs = np.array(uvs, dtype=np.float32)

            for vertices_per_key in vertices_per_key_per_anim:
                vertices_per_key = np.array(vertices_per_key, dtype=np.float32)

            if np.isnan(uvs).any():
                uvs = np.nan_to_num(uvs)

            for vertices_per_key in vertices_per_key_per_anim:
                if np.isnan(vertices_per_key).any():
                    raise ValueError("vertices_per_key contains nan")

            gltf_primitive = GltfPrimitive(
                indices=primitive_indices,
                vertices=vertices,
                baf_to_vertices_per_key=vertices_per_key_per_anim,
                normals=normals,
                uvs=uvs,
                texture_index=texture_index,
            )
            gltf_primitives.append(gltf_primitive)

        return gltf_mesh
