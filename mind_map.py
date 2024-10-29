from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, NamedTuple
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.colors import to_rgb
from abc import ABC, abstractmethod


class Position(NamedTuple):
    """Represents a 2D position"""

    x: float
    y: float


class ColorScheme(ABC):
    """Abstract base class for color schemes"""

    @abstractmethod
    def get_color(self, index: int, level: int) -> str:
        """Get color for a node based on its index and level"""
        pass


class GradientColorScheme(ColorScheme):
    """Implements a gradient-based color scheme"""

    def __init__(self, base_colors: Dict[int, str]):
        self.base_colors = base_colors

    def get_color(self, index: int, level: int) -> str:
        if level == -1:
            return '#182536'
        
        if level == 0:
            base_colors = [
                '#8A4FFF', '#32B679',
                '#FF8C82', '#FFA726', '#4B7BF5'
            ]
            return base_colors[index % len(base_colors)]
        
        parent_color = self.get_color(index, level - 1)
        base_rgb = np.array(to_rgb(parent_color))
        white_rgb = np.array([1, 1, 1])
        mix_factor = min((level - 1) * 0.15, 0.6)
        final_rgb = base_rgb * (1 - mix_factor) + white_rgb * mix_factor
        return f'#{int(final_rgb[0]*255):02x}{int(final_rgb[1]*255):02x}{int(final_rgb[2]*255):02x}'


@dataclass
class MindMapConfig:
    """Configuration settings for mind map visualization."""

    width: int = 15
    height: int = 10
    dpi: int = 100
    x_limits: Tuple[int, int] = (-0.5, 11.5)
    y_limits: Tuple[int, int] = (-4.5, 4.5)
    text_bar_height: float = 0.3
    text_padding: float = 0.2
    color_scheme: ColorScheme = field(default_factory=lambda: GradientColorScheme({}))


@dataclass
class Node:
    """Represents a node in the mind map."""

    text: str
    children: List['Node'] = field(default_factory=list)
    position: Optional[Position] = None
    color: Optional[str] = None
    text_width: Optional[float] = None


class BezierCurve:
    """Value object for Bezier curve calculations"""

    @staticmethod
    def calculate_points(start: Position, end: Position, points: int = 100) -> np.ndarray:
        distance_x = end.x - start.x
        control1 = Position(start.x + distance_x * 0.5, start.y)
        control2 = Position(start.x + distance_x * 0.5, end.y)
        
        t = np.linspace(0, 1, points)
        curve_points = np.array([
            (1-t)**3 * start.x + 3*(1-t)**2*t * control1.x + 3*(1-t)*t**2 * control2.x + t**3 * end.x,
            (1-t)**3 * start.y + 3*(1-t)**2*t * control1.y + 3*(1-t)*t**2 * control2.y + t**3 * end.y
        ])
        return curve_points.T


class NodeRenderer:
    """Handles the rendering of individual nodes"""

    def __init__(self, ax, config: MindMapConfig):
        self.ax = ax
        self.config = config
        self.fig = ax.figure
        if not hasattr(self.fig.canvas, 'renderer'):
            self.fig.canvas.draw()
        self.renderer = self.fig.canvas.get_renderer()

    def render_node(self, position: Position, text: str, color: str, level: int) -> None:
        is_root = level == -1
        bar_height = self.config.text_bar_height * 0.5 if not is_root else self.config.text_bar_height * 2

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
        return 16 if level == -1 else 14

    def _render_text(self, position: Position, text: str, level: int) -> None:
        is_root = level == -1
        y_offset = self.config.text_bar_height * (0.75 if not is_root else 0)
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
        """Calculate the width of text in data coordinates with minimal padding"""
        text_obj = Text(
            0, 0, text,
            fontsize=fontsize,
            figure=self.fig
        )
        bbox = text_obj.get_window_extent(self.renderer)
        bbox_data = bbox.transformed(self.ax.transData.inverted())
        return bbox_data.width + self.config.text_padding * 2


class ConnectionRenderer:
    """Handles the rendering of connections between nodes"""

    def __init__(self, ax):
        self.ax = ax
        self.bezier = BezierCurve()

    def render_connection(self, start: Position, end: Position, color: str) -> None:
        curve_points = self.bezier.calculate_points(start, end)
        self.ax.plot(
            curve_points[:, 0],
            curve_points[:, 1],
            color=color,
            linewidth=2,
            alpha=1,
            solid_capstyle='round',
            zorder=1
        )


class MindMapLayout:
    """Handles the layout calculations for the mind map"""

    def __init__(self, config: MindMapConfig):
        self.config = config
        self.max_depth = 0
        self.nodes_by_level = {}
        self.base_level_height = 9
        self.node_renderer = None

    def set_renderer(self, node_renderer: NodeRenderer):
        """Set the node renderer to calculate text dimensions"""
        self.node_renderer = node_renderer
    
    def _get_node_height(self, text: str, level: int) -> float:
        """Calculate the total height needed for a node including its text and padding"""
        if self.node_renderer is None:
            raise RuntimeError("Node renderer must be set before layout calculation")

        # Get text height in data coordinates
        text_obj = Text(
            0, 0, text,
            fontsize=self.node_renderer._get_font_size(level),
            figure=self.node_renderer.fig
        )
        bbox = text_obj.get_window_extent(self.node_renderer.renderer)
        bbox_data = bbox.transformed(self.node_renderer.ax.transData.inverted())
        text_height = bbox_data.height
        
        # Add padding and bar height
        is_root = level == -1
        bar_height = self.config.text_bar_height * (2 if is_root else 0.5)
        
        return max(text_height, bar_height) + (self.config.text_padding * 2)

    def calculate_layout(self, root: Node) -> None:
        """Calculate initial position for root node and trigger children layout"""
        if self.node_renderer is None:
            raise RuntimeError("Node renderer must be set before layout calculation")
            
        # Reset tracking variables
        self.max_depth = 0
        self.nodes_by_level = {}
        
        # Calculate tree metrics
        self._analyze_tree(root, 0)
        
        # Set root position
        root.position = Position(0, 0)
        
        if root.children:
            self._layout_level(root.children, root.position, root.text_width)
    
    def _analyze_tree(self, node: Node, depth: int) -> None:
        """Analyze tree structure to gather metrics for layout calculations"""
        if depth not in self.nodes_by_level:
            self.nodes_by_level[depth] = 0
        self.nodes_by_level[depth] += 1
        
        self.max_depth = max(self.max_depth, depth)
        
        for child in node.children:
            self._analyze_tree(child, depth + 1)
    
    def _analyze_tree(self, node: Node, depth: int) -> None:
        """Analyze tree structure to gather metrics for layout calculations"""
        if depth not in self.nodes_by_level:
            self.nodes_by_level[depth] = 0
        self.nodes_by_level[depth] += 1
        
        self.max_depth = max(self.max_depth, depth)
        
        for child in node.children:
            self._analyze_tree(child, depth + 1)
    
    def _calculate_level_height(self, nodes: List[Node], depth: int, parent_height: float) -> float:
        """Calculate appropriate height for a level based on depth, node count, and text heights"""
        nodes_at_level = len(nodes)
        
        # Calculate maximum node height at this level
        max_node_height = max(
            self._get_node_height(node.text, depth)
            for node in nodes
        )
        
        # Minimum required height based on node heights
        min_required_height = max_node_height * nodes_at_level
        
        # Adjust base height based on number of nodes
        if nodes_at_level > 6:
            base_height = parent_height * 1.2
        else:
            base_height = parent_height * 0.8
        
        # Adjust based on depth
        depth_factor = max(0.4, 1 - (depth * 0.15))
        
        # Node count adjustment
        if nodes_at_level <= 2:
            node_factor = 0.5
        elif nodes_at_level <= 4:
            node_factor = 0.7
        elif nodes_at_level <= 6:
            node_factor = 0.9
        else:
            node_factor = 1.0
            
        calculated_height = base_height * depth_factor * node_factor
        
        # Ensure we have at least enough height for all nodes plus minimum spacing
        return max(calculated_height, min_required_height + (max_node_height * 0.5))
    
    def _calculate_node_spacing(self, nodes: List[Node], level_height: float, depth: int) -> float:
        """Calculate appropriate spacing between nodes based on count, level height, and text heights"""
        num_nodes = len(nodes)
        if num_nodes <= 1:
            return 0
        
        # Calculate maximum node height at this level
        max_node_height = max(
            self._get_node_height(node.text, depth)
            for node in nodes
        )
        
        # Minimum spacing should be at least 20% of the node height
        min_spacing = max_node_height * 0.2
        
        # Calculate base spacing
        base_spacing = max(
            level_height / (num_nodes - 1),
            min_spacing
        )
        
        # Adjust spacing based on number of nodes
        if num_nodes <= 2:
            spacing_factor = 0.5
        elif num_nodes <= 4:
            spacing_factor = 0.7
        elif num_nodes <= 6:
            spacing_factor = 0.85
        else:
            spacing_factor = 1.0
            
        # Depth adjustment - less aggressive reduction for higher node counts
        if num_nodes > 6:
            depth_factor = max(0.8, 1 - (depth * 0.05))
        else:
            depth_factor = max(0.4, 1 - (depth * 0.1))
        
        # Ensure we never go below minimum spacing
        return max(
            base_spacing * spacing_factor * depth_factor,
            min_spacing
        )
    
    def _layout_level(self, nodes: List[Node], parent_pos: Position, parent_width: float, depth: int = 1, parent_height: float = None) -> None:
        """Layout nodes at a specific level with dynamic spacing"""
        if not nodes:
            return

        if parent_height is None:
            parent_height = self.base_level_height

        level_height = self._calculate_level_height(nodes, depth, parent_height)
        spacing = self._calculate_node_spacing(nodes, level_height, depth)
        
        # Calculate total height needed for all nodes
        total_height = spacing * (len(nodes) - 1) if len(nodes) > 1 else 0
        
        # Calculate starting Y position to center the nodes
        start_y = parent_pos.y + (total_height / 2)
        
        # Calculate X position with consistent spacing from parent
        next_x = parent_pos.x + parent_width + 1.5

        for i, node in enumerate(nodes):
            # Calculate Y position
            node_y = start_y - (i * spacing)
            node.position = Position(next_x, node_y)

            if node.children:
                self._layout_level(
                    node.children,
                    node.position,
                    node.text_width,
                    depth + 1,
                    level_height
                )


class MindMap:
    """Main class for creating and managing mind maps."""
    
    def __init__(self, config: Optional[MindMapConfig] = None):
        self.config = config or MindMapConfig()
        self.fig: Optional[Figure] = None
        self.ax = None
        self.node_renderer: Optional[NodeRenderer] = None
        self.connection_renderer: Optional[ConnectionRenderer] = None
        self.layout_manager: Optional[MindMapLayout] = None
        self._setup_figure()
    
    def _setup_figure(self) -> None:
        """Initialize the matplotlib figure and axes."""
        plt.close('all')
        
        self.fig = plt.figure(figsize=(self.config.width, self.config.height), 
                            dpi=self.config.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(*self.config.x_limits)
        self.ax.set_ylim(*self.config.y_limits)
        self.ax.axis('off')
        
        # Ensure the figure has a canvas and renderer
        if not self.fig.canvas:
            self.fig.canvas = plt.get_current_fig_manager().canvas
        
        # Initialize renderers and layout manager
        self.node_renderer = NodeRenderer(self.ax, self.config)
        self.connection_renderer = ConnectionRenderer(self.ax)
        self.layout_manager = MindMapLayout(self.config)
    
    def _calculate_node_dimensions(self, node: Node, level: int = 0) -> None:
        """Pre-calculate text widths for all nodes."""
        node.text_width = self.node_renderer.get_text_width(
            node.text, 
            self.node_renderer._get_font_size(level)
        )
        for child in node.children:
            self._calculate_node_dimensions(child, level + 1)
    
    def _convert_to_nodes(self, data: List[Tuple[str, List]]) -> List[Node]:
        """Convert raw data structure to Node objects."""
        return [
            Node(text, self._convert_to_nodes(children)) 
            for text, children in data
        ]
    
    def _assign_colors(self, node: Node, level: int = -1, index: int = 0) -> None:
        """Assign colors to all nodes in the tree."""
        node.color = self.config.color_scheme.get_color(index, level)
        for i, child in enumerate(node.children):
            self._assign_colors(child, level + 1, i)
    
    def _render_tree(self, node: Node, level: int = -1, parent_pos: Optional[Position] = None) -> None:
        """Render the entire tree structure recursively."""
        if parent_pos is not None:
            self.connection_renderer.render_connection(
                parent_pos,
                node.position,
                node.color
            )
        
        self.node_renderer.render_node(
            node.position,
            node.text,
            node.color,
            level
        )
        
        end_pos = Position(
            node.position.x + node.text_width,
            node.position.y
        )
        
        for child in node.children:
            self._render_tree(child, level + 1, end_pos)
    
    def create(self, data: Tuple[str, List]) -> Figure:
        """Create a mind map from the given data structure."""
        root_text, children = data
        root_node = Node(root_text, self._convert_to_nodes(children))
        
        # Calculate dimensions
        self._calculate_node_dimensions(root_node)
        
        # Set the renderer in the layout manager
        self.layout_manager.set_renderer(self.node_renderer)
        
        # Calculate layout
        self.layout_manager.calculate_layout(root_node)
        
        # Assign colors
        self._assign_colors(root_node)
        
        # Render the tree
        self._render_tree(root_node)
        
        # Ajustar los márgenes de la figura
        self.fig.tight_layout(pad=0.5)
        
        return self.fig
    
    def save(self, filename: str, **kwargs) -> None:
        """Save the mind map to a file"""
        if self.fig is None:
            raise RuntimeError("No mind map has been created yet")
        self.fig.savefig(filename, **kwargs)
    
    def show(self) -> None:
        """Display the mind map."""
        if self.fig is None:
            raise RuntimeError("No mind map has been created yet")
        plt.show()
