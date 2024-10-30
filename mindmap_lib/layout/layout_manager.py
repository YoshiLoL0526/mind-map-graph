from typing import List, TYPE_CHECKING
from matplotlib.text import Text

from mindmap_lib.layout import Position

if TYPE_CHECKING:
    from mindmap_lib.core import Node, MindMapConfig
    from mindmap_lib.rendering import NodeRenderer


class MindMapLayout:
    """
    Handles the layout calculation for the mind map with adaptive node sizing.
    """
    def __init__(self, config: 'MindMapConfig'):
        self.config = config
        self.max_depth = 0
        self.nodes_by_level = {}
        self.base_level_height = 7
        self.node_renderer = None
        self.min_spacing = 0.3

    def set_renderer(self, node_renderer: 'NodeRenderer'):
        """Set the node renderer for the layout"""
        self.node_renderer = node_renderer

    def _calculate_subtree_height(self, node: 'Node') -> float:
        if node is None:
            return 0.0
            
        height = self._get_node_height(node.text, -1 if node.position is None else 1)
        
        if not node.children:
            return max(height, 0.6)
            
        children_height = self._calculate_children_height(node.children)
        return max(height, children_height)
    
    def _calculate_children_height(self, children: List['Node']) -> float:
        if not children:
            return 0.0
            
        total_height = sum(self._calculate_subtree_height(child) for child in children if child is not None)
        spacing = max(self.min_spacing, 0.4)
        total_height += (len(children) - 1) * spacing
        return total_height

    def _get_node_height(self, text: str, level: int) -> float:
        if self.node_renderer is None:
            raise RuntimeError("Node renderer must be set before layout calculation")
            
        text_obj = Text(
            0, 0, text,
            fontsize=self.node_renderer.get_font_size(level),
            figure=self.node_renderer.fig
        )
        bbox = text_obj.get_window_extent(self.node_renderer.renderer)
        bbox_data = bbox.transformed(self.node_renderer.ax.transData.inverted())
        return bbox_data.height

    def _analyze_tree(self, node: 'Node', depth: int) -> None:
        if node is None:
            return
            
        if depth not in self.nodes_by_level:
            self.nodes_by_level[depth] = 0
        self.nodes_by_level[depth] += 1
        
        self.max_depth = max(self.max_depth, depth)
        scaled_font_size = self.node_renderer.get_font_size(depth)
        node.text_width = self.node_renderer.get_text_width(node.text, scaled_font_size)
        
        for child in node.children:
            if child is not None:
                self._analyze_tree(child, depth + 1)

    def _layout_children(self, parent: 'Node') -> None:
        if not parent or not parent.children:
            return

        total_height = self._calculate_children_height(parent.children)
        spacing = max(self.min_spacing, 1.5)
        child_x = parent.position.x + parent.text_width + spacing
        
        start_y = parent.position.y + (total_height / 2)
        current_y = start_y
        
        for child in parent.children:
            if child is not None:
                subtree_height = self._calculate_subtree_height(child)
                child.position = Position(child_x, current_y - (subtree_height / 2))
                self._layout_children(child)
                spacing = max(self.min_spacing, 0.4)
                current_y -= (subtree_height + spacing)

    def _calculate_total_width(self, node: 'Node', level: int = 0) -> float:
        """Calculate total width needed for the tree"""
        if node is None or not hasattr(node, 'text_width'):
            return 0.0
            
        if not node.children:
            return node.text_width

        children_widths = [self._calculate_total_width(child, level + 1) 
                         for child in node.children 
                         if child is not None]
        
        children_width = max(children_widths) if children_widths else 0.0
        return (node.text_width + children_width + 1.5)

    def calculate_layout(self, root: 'Node') -> None:
        """
        Calculate the layout for the entire mind map with adaptive sizing.
        """
        if root is None:
            return
            
        self.max_depth = 0
        self.nodes_by_level = {}
        self._analyze_tree(root, -1)
        root.position = Position(0, 0)
        
        if root.children:
            self._layout_children(root)
