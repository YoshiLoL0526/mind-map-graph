from dataclasses import dataclass, field

from mindmap_lib.rendering import ColorScheme, GradientColorScheme


@dataclass
class MindMapConfig:
    """
    Configuration settings for mind map visualization.
    """
    width: int = 20
    height: int = 12
    dpi: int = 100
    max_font_size = 14
    min_font_size = 12
    text_bar_height: float = 0.3
    text_padding: float = 0.2
    color_scheme: ColorScheme = field(default_factory=lambda: GradientColorScheme({
        0: "#4285f4",  # Google Blue
        1: "#34a853",  # Google Green
        2: "#fbbc05",  # Google Yellow
        3: "#ea4335"   # Google Red
    }))