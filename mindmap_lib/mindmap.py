import json
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from mindmap_lib.core import MindMapConfig, Node
from mindmap_lib.layout import MindMapLayout, Position
from mindmap_lib.rendering import NodeRenderer, ConnectionRenderer


class MindMap:
    """
    Main class for creating and managing mind maps.
    """
    def __init__(self, config: Optional[MindMapConfig] = None):
        self.config = config or MindMapConfig()
        self.fig: Optional[Figure] = None
        self.ax = None
        self.node_renderer = None
        self.connection_renderer = None
        self.layout_manager = None
    
    def _setup_figure(self) -> None:
        plt.close('all')
        
        self.fig = plt.figure(figsize=(self.config.width, self.config.height), 
                            dpi=self.config.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(*self.config.x_limits)
        self.ax.set_ylim(*self.config.y_limits)
        self.ax.axis('off')
        
        # Adjusted margins
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        
        if not self.fig.canvas:
            self.fig.canvas = plt.get_current_fig_manager().canvas
        
        self.fig.canvas.draw()
        
        self.node_renderer = NodeRenderer(self.ax, self.config)
        self.connection_renderer = ConnectionRenderer(self.ax)
        self.layout_manager = MindMapLayout(self.config)
        self.layout_manager.set_renderer(self.node_renderer)
    
    def _convert_to_nodes(self, data: List[Tuple[str, List]]) -> List[Node]:
        return [Node(text, self._convert_to_nodes(children)) 
                for text, children in data]
    
    def _assign_colors(self, node: Node, level: int = -1, index: int = 0) -> None:
        node.color = self.config.color_scheme.get_color(index, level)
        for i, child in enumerate(node.children):
            self._assign_colors(child, level + 1, i)
    
    def _render_tree(self, node: Node, level: int = -1, parent_pos: Optional[Position] = None) -> None:
        """Render all the tree recursively"""
        if parent_pos is not None:
            self.connection_renderer.render_connection(parent_pos, node.position, node.color)
        
        self.node_renderer.render_node(node.position, node.text, node.color, level)
        
        end_pos = Position(node.position.x + node.text_width, node.position.y)
        
        for child in node.children:
            self._render_tree(child, level + 1, end_pos)
    
    def _create_mind_map(self, root_node: Node) -> Figure:
        """
        Internal method to create the mind map from a root node.
        """
        self._setup_figure()
        self.layout_manager.calculate_layout(root_node)
        self._assign_colors(root_node)
        self._render_tree(root_node)
        return self.fig

    def create_from_json(self, json_data: str) -> Figure:
        """
        Create mind map from JSON string.
        
        Args:
            json_data (str): JSON string containing mind map data
            
        Returns:
            Figure: Generated mind map figure
        """
        data = json.loads(json_data)
        root_node = Node.from_dict(data)
        return self._create_mind_map(root_node)
    
    def create_from_file(self, json_file: str) -> Figure:
        """
        Create mind map from JSON file.
        
        Args:
            json_file (str): Path to JSON file
            
        Returns:
            Figure: Generated mind map figure
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        root_node = Node.from_dict(data)
        return self._create_mind_map(root_node)
    
    def save(self, filename: str, **kwargs) -> None:
        """
        Save the mind map to a file.
        
        Args:
            filename (str): Output filename
            **kwargs: Additional arguments for savefig
        """
        if self.fig is None:
            raise RuntimeError("No mind map has been created yet")
        self.fig.savefig(filename, **kwargs)
    
    def show(self) -> None:
        """Display the mind map"""
        if self.fig is None:
            raise RuntimeError("No mind map has been created yet")
        plt.show()
