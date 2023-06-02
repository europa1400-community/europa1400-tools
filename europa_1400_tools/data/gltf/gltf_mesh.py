from dataclasses import dataclass

from europa_1400_tools.data.gltf.gltf_primitive import GltfPrimitive


@dataclass
class GltfMesh:
    """Class representing a mesh in a gLTF file."""

    name: str
    primitives: list[GltfPrimitive]
