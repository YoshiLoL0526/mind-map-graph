import numpy as np
from typing import Dict
from abc import ABC, abstractmethod
from matplotlib.colors import to_rgb


class ColorScheme(ABC):
    """
    Abstract base class for color schemes used in the mind map.
    Defines the interface for getting colors based on node position and level.
    """
    @abstractmethod
    def get_color(self, index: int, level: int) -> str:
        pass


class GradientColorScheme(ColorScheme):
    """
    Implements a gradient-based color scheme where colors become lighter as levels increase.
    """
    def __init__(self, base_colors: Dict[int, str]):
        self.base_colors = base_colors

    def get_color(self, index: int, level: int) -> str:
        """
        Get color for a node with gradient effect based on level.
        
        Args:
            index (int): Node index within its level
            level (int): Depth level in the mind map
            
        Returns:
            str: Color in hex format with gradient effect applied
        """
        if level == -1:  # Root node color
            return '#182536'
        
        if level == 0:  # First level uses base colors
            return self.base_colors[index % len(self.base_colors)]
        
        # Apply gradient effect for deeper levels
        parent_color = self.get_color(index, level - 1)
        base_rgb = np.array(to_rgb(parent_color))
        white_rgb = np.array([1, 1, 1])
        mix_factor = min((level - 1) * 0.15, 0.6)
        final_rgb = base_rgb * (1 - mix_factor) + white_rgb * mix_factor
        
        return f'#{int(final_rgb[0]*255):02x}{int(final_rgb[1]*255):02x}{int(final_rgb[2]*255):02x}'


class EnhancedGradientScheme(ColorScheme):
    """
    Implements an enhanced gradient color scheme with 5 distinct branch colors
    and sophisticated lightening based on depth level.
    """
    def __init__(self):
        # Define 5 vibrant base colors for main branches (in hex)
        self.base_colors = {
            0: "#FF6B6B",  # Coral Red
            1: "#4ECDC4",  # Turquoise
            2: "#45B7D1",  # Sky Blue
            3: "#96CEB4",  # Sage Green
            4: "#FFEEAD",  # Soft Yellow
        }
        
        # Control parameters for gradient effect
        self.max_lightness = 0.8  # Maximum lightness increase
        self.lightness_step = 0.15  # How much lighter each level becomes
        self.saturation_decay = 0.1  # How much saturation decreases per level
        
    def _adjust_color_component(self, base: float, target: float, factor: float) -> float:
        """
        Adjusts a color component (R, G, or B) towards a target value based on a factor.
        
        Args:
            base (float): Original color component value (0-1)
            target (float): Target value to adjust towards (usually 1 for lightening)
            factor (float): Adjustment factor (0-1)
            
        Returns:
            float: Adjusted color component value
        """
        return base + (target - base) * factor
    
    def _calculate_gradient_factor(self, level: int) -> float:
        """
        Calculates the gradient factor based on the depth level.
        Implements a non-linear gradient progression.
        
        Args:
            level (int): Depth level in the mind map
            
        Returns:
            float: Gradient factor between 0 and 1
        """
        if level <= 0:
            return 0
        
        # Non-linear gradient progression
        base_factor = min(level * self.lightness_step, self.max_lightness)
        # Add slight randomization to avoid monotonous progression
        random_variation = np.random.uniform(-0.05, 0.05)
        return min(max(base_factor + random_variation, 0), self.max_lightness)
    
    def get_color(self, index: int, level: int) -> str:
        """
        Get color for a node with enhanced gradient effect based on level.
        
        Args:
            index (int): Node index within its level
            level (int): Depth level in the mind map
            
        Returns:
            str: Color in hex format with enhanced gradient effect applied
        """
        if level == -1:  # Root node
            return '#2C3E50'  # Dark blue-grey
        
        if level == 0:  # First level - use base colors
            return self.base_colors[index % len(self.base_colors)]
        
        # Get the base color from parent branch
        branch_index = index % len(self.base_colors)
        base_color = np.array(to_rgb(self.base_colors[branch_index]))
        
        # Calculate gradient factor with non-linear progression
        gradient_factor = self._calculate_gradient_factor(level)
        
        # Apply sophisticated color adjustment
        adjusted_color = np.array([
            self._adjust_color_component(base_color[0], 1.0, gradient_factor),
            self._adjust_color_component(base_color[1], 1.0, gradient_factor),
            self._adjust_color_component(base_color[2], 1.0, gradient_factor)
        ])
        
        # Apply saturation decay
        saturation_factor = max(1 - (level * self.saturation_decay), 0.2)
        adjusted_color = (adjusted_color - 0.5) * saturation_factor + 0.5
        
        # Ensure color values are within valid range
        adjusted_color = np.clip(adjusted_color, 0, 1)
        
        # Convert to hex format
        return f'#{int(adjusted_color[0]*255):02x}{int(adjusted_color[1]*255):02x}{int(adjusted_color[2]*255):02x}'