import numpy as np

from mindmap_lib.layout import Position


class BezierCurve:
    """
    Handles Bezier curve calculations for connection lines between nodes.
    """
    @staticmethod
    def calculate_points(start: Position, end: Position, points: int = 100) -> np.ndarray:
        """
        Calculate points for a cubic Bezier curve between two positions.
        """
        distance_x = end.x - start.x
        control1 = Position(start.x + distance_x * 0.4, start.y)
        control2 = Position(start.x + distance_x * 0.6, end.y)
        
        t = np.linspace(0, 1, points)
        curve_points = np.array([
            (1-t)**3 * start.x + 3*(1-t)**2*t * control1.x + 3*(1-t)*t**2 * control2.x + t**3 * end.x,
            (1-t)**3 * start.y + 3*(1-t)**2*t * control1.y + 3*(1-t)*t**2 * control2.y + t**3 * end.y
        ])
        return curve_points.T


class ConnectionRenderer:
    """Handles rendering of connections between nodes"""
    def __init__(self, ax):
        self.ax = ax
        self.bezier = BezierCurve()

    def render_connection(self, start: Position, end: Position, color: str) -> None:
        """
        Render a connection between two nodes.
        """
        curve_points = self.bezier.calculate_points(start, end)
        self.ax.plot(
            curve_points[:, 0],
            curve_points[:, 1],
            color=color,
            linewidth=1.5,
            alpha=0.8,
            solid_capstyle='round',
            zorder=1
        )