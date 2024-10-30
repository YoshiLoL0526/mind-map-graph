from dataclasses import dataclass, field
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mindmap_lib.layout import Position


@dataclass
class Node:
    """
    Represents a node in the mind map.
    """
    text: str
    children: List['Node'] = field(default_factory=list)
    position: Optional['Position'] = None
    color: Optional[str] = None
    text_width: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """
        Create a Node from a dictionary representation.
        """
        return cls(
            text=data['text'],
            children=[cls.from_dict(child) for child in data.get('children', [])]
        )