from typing import List, TYPE_CHECKING
from matplotlib.text import Text

from mindmap_lib.layout import Position

if TYPE_CHECKING:
    from mindmap_lib.core import Node, MindMapConfig
    from mindmap_lib.rendering import NodeRenderer


class MindMapLayout:
    """
    Handles the layout calculation for the mind map.
    """
    def __init__(self, config: 'MindMapConfig'):
        self.config = config
        self.max_depth = 0
        self.nodes_by_level = {}
        self.base_level_height = 7
        self.node_renderer = None

    def set_renderer(self, node_renderer: 'NodeRenderer'):
        """Set the node renderer for the layout"""
        self.node_renderer = node_renderer
    
    def _calculate_subtree_height(self, node: 'Node') -> float:
        height = self._get_node_height(node.text, -1 if node.position is None else 1)
        
        if not node.children:
            return max(height, 0.6)
            
        children_height = self._calculate_children_height(node.children)
        return max(height, children_height)
    
    def _calculate_children_height(self, children: List['Node']) -> float:
        if not children:
            return 0
            
        total_height = sum(self._calculate_subtree_height(child) for child in children)
        total_height += (len(children) - 1) * 0.4
        return total_height

    def _scale_layout(self, nodes: List['Node'], total_height: float) -> float:
        available_height = self.config.y_limits[1] - self.config.y_limits[0] - 2.0  # Increased margin
        return min(1.0, available_height / total_height)
    
    def _get_node_height(self, text: str, level: int) -> float:
        if self.node_renderer is None:
            raise RuntimeError("Node renderer must be set before layout calculation")
            
        text_obj = Text(
            0, 0, text,
            fontsize=self.node_renderer._get_font_size(level),
            figure=self.node_renderer.fig
        )
        bbox = text_obj.get_window_extent(self.node_renderer.renderer)
        bbox_data = bbox.transformed(self.node_renderer.ax.transData.inverted())
        return bbox_data.height + (self.config.text_padding * 1.5)  # Reduced padding multiplier
    
    def _analyze_tree(self, node: 'Node', depth: int) -> None:
        if depth not in self.nodes_by_level:
            self.nodes_by_level[depth] = 0
        self.nodes_by_level[depth] += 1
        
        self.max_depth = max(self.max_depth, depth)
        node.text_width = self.node_renderer.get_text_width(
            node.text, 
            self.node_renderer._get_font_size(depth)
        )
        
        for child in node.children:
            self._analyze_tree(child, depth + 1)

    def _layout_children(self, parent: 'Node') -> None:
        if not parent.children:
            return

        total_height = self._calculate_children_height(parent.children)
        child_x = parent.position.x + parent.text_width + 1.5  # Reduced spacing from 2.0
        
        start_y = parent.position.y + (total_height / 2)
        current_y = start_y
        
        for child in parent.children:
            subtree_height = self._calculate_subtree_height(child)
            child.position = Position(child_x, current_y - (subtree_height / 2))
            self._layout_children(child)
            current_y -= (subtree_height + 0.4)  # Reduced spacing from 0.5
    
    def _calculate_total_width(self, node: 'Node', level: int = 0) -> float:
        """Calculate total width needed for the tree"""
        if not node.children:
            return node.text_width
            
        children_width = max(self._calculate_total_width(child, level + 1) 
                           for child in node.children)
        return (node.text_width + children_width)
    
    def calculate_layout(self, root: 'Node') -> None:
        """
        Calculate the layout for the entire mind map.
        """
        self.max_depth = 0
        self.nodes_by_level = {}
        self._analyze_tree(root, -1)
        root.position = Position(self.config.x_limits[0] + 0.8, 0)
        
        if root.children:
            # Calculate total width needed
            max_width = self._calculate_total_width(root)
            
            # Adjust x_limits if needed
            if max_width > (self.config.x_limits[1] - self.config.x_limits[0]):
                self.config.x_limits = (self.config.x_limits[0], 
                                      self.config.x_limits[0] + max_width + 2.0)
            
            self._layout_children(root)
