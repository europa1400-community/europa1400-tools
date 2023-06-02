from dataclasses import dataclass

from europa_1400_tools.data.bgf.bgf_model import BgfModel
from europa_1400_tools.data.bgf.bgf_texture_mapping import BgfTextureMapping
from europa_1400_tools.data.face import Face
from europa_1400_tools.data.vertex import Vertex


@dataclass
class WavefrontModel:
    """Class representing a wavefront model."""

    normals: list[Vertex]
    faces: list[Face]
    materials: list[str]
    vertices: list[Vertex]
    texture_mappings: list[BgfTextureMapping]

    @classmethod
    def from_bgf_model(
        cls, bgf_model: BgfModel, materials: list[str]
    ) -> "WavefrontModel":
        """Converts a bgf model to a wavefront model."""

        if (
            len(bgf_model.vertices)
            != len(bgf_model.faces)
            != len(bgf_model.normals)
            != len(bgf_model.texture_mappings)
            != len(materials)
        ):
            raise ValueError("Amount of model elements do not match.")

        return WavefrontModel(
            normals=bgf_model.normals,
            faces=bgf_model.faces,
            materials=materials,
            vertices=bgf_model.vertices,
            texture_mappings=bgf_model.texture_mappings,
        )
