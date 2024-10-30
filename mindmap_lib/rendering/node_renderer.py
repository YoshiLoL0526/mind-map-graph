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
        bar_height = self.config.text_bar_height * (3 if is_root else 1.0)
        text_width = self.get_text_width(text, self.get_font_size(level))
        
        if is_root:
            rect = FancyBboxPatch(
                (position.x - self.config.text_padding,
                 position.y - bar_height/2),
                text_width + self.config.text_padding * 2,
                bar_height,
                boxstyle="round,pad=0.1,rounding_size=0.2",
                facecolor='#182536',
                edgecolor='none',
                alpha=1,
                zorder=2
            )
        else:
            rect = Rectangle(
                (position.x - self.config.text_padding,
                 position.y - bar_height/2),
                text_width + self.config.text_padding * 2,
                bar_height,
                facecolor=color,
                edgecolor='none',
                alpha=1,
                zorder=2
            )
        self.ax.add_patch(rect)
        
        self._render_text(position, text, level, text_width, bar_height)

    def get_font_size(self, level: int) -> int:
        """Get font size based on node level"""
        return self.config.max_font_size if level == -1 else self.config.min_font_size

    def _render_text(self, position: Position, text: str, level: int, text_width: float, bar_height: float) -> None:
        """Render text for a node"""
        is_root = level == -1
        
        if is_root:
            self.ax.text(
                position.x + text_width/2,
                position.y,
                text,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=self.get_font_size(level),
                fontweight='bold',
                color='white',
                zorder=3
            )
        else:
            y_offset = 0.3
            self.ax.text(
                position.x + text_width/2,
                position.y + y_offset,
                text,
                horizontalalignment='center',
                verticalalignment='bottom',
                fontsize=self.get_font_size(level),
                fontweight='normal',
                color='black',
                zorder=3
            )

    def get_text_width(self, text: str, fontsize: int) -> float:
        """Calculate width of text given font size"""
        text_obj = Text(0, 0, text, fontsize=fontsize, figure=self.fig)
        bbox = text_obj.get_window_extent(self.renderer)
        bbox_data = bbox.transformed(self.ax.transData.inverted())
        return bbox_data.width
