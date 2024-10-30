from typing import TYPE_CHECKING

from matplotlib.text import Text
from matplotlib.patches import Rectangle, FancyBboxPatch

from mindmap_lib.layout import Position

if TYPE_CHECKING:
    from mindmap_lib.core import MindMapConfig


class NodeRenderer:
    """
    Handles the rendering of individual nodes in the mind map.
    """
    def __init__(self, ax, config: 'MindMapConfig'):
        self.ax = ax
        self.config = config
        self.fig = ax.figure
        if not hasattr(self.fig.canvas, 'renderer'):
            self.fig.canvas.draw()
        self.renderer = self.fig.canvas.get_renderer()

    def render_node(self, position: Position, text: str, color: str, level: int) -> None:
        """
        Render a single node with its background and text.
        """
        is_root = level == -1
        bar_height = self.config.text_bar_height * (1.8 if is_root else 0.5)

        text_width = self.get_text_width(text, self._get_font_size(level))
        
        if is_root:
            rect = FancyBboxPatch(
                (position.x, position.y - bar_height/2),
                text_width,
                bar_height,
                boxstyle="round,pad=0.1,rounding_size=0.3",
                facecolor='#182536',
                edgecolor='none',
                alpha=1,
                zorder=2
            )
        else:
            rect = Rectangle(
                (position.x, position.y - bar_height/2),
                text_width,
                bar_height,
                facecolor=color,
                edgecolor='none',
                alpha=1,
                zorder=2
            )
        self.ax.add_patch(rect)
        
        self._render_text(position, text, level)

    def _get_font_size(self, level: int) -> int:
        """Get font size based on node level"""
        return 14 if level == -1 else 12

    def _render_text(self, position: Position, text: str, level: int) -> None:
        """Render text for a node"""
        is_root = level == -1
        y_offset = self.config.text_bar_height * (0.6 if not is_root else 0)
        self.ax.text(
            position.x + self.config.text_padding,
            position.y + y_offset,
            text,
            horizontalalignment='left',
            verticalalignment='center',
            fontsize=self._get_font_size(level),
            fontweight='bold' if is_root else 'normal',
            color='white' if is_root else 'black',
            zorder=3
        )

    def get_text_width(self, text: str, fontsize: int) -> float:
        """Calculate width of text given font size"""
        text_obj = Text(0, 0, text, fontsize=fontsize, figure=self.fig)
        bbox = text_obj.get_window_extent(self.renderer)
        bbox_data = bbox.transformed(self.ax.transData.inverted())
        return bbox_data.width + self.config.text_padding * 2