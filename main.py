from mindmap import MindMap, MindMapConfig, ColorScheme

# Define your mind map structure
# Format: (root_text, [(child1_text, [grandchildren1]), (child2_text, [grandchildren2]), ...])
mind_map_data = (
    "Project Planning",
    [
        ("Research", [
            ("Market Analysis", []),
            ("Competitor Review", []),
            ("User Surveys", [])
        ]),
        ("Design", [
            ("Wireframes", []),
            ("UI/UX", []),
            ("Prototypes", [])
        ]),
        ("Development", [
            ("Frontend", []),
            ("Backend", []),
            ("Testing", [])
        ]),
        ("Launch", [
            ("Marketing", []),
            ("Deployment", []),
            ("Monitoring", [])
        ])
    ]
)


class CustomColorScheme(ColorScheme):
    def get_color(self, index: int, level: int) -> str:
        # Your color logic here
        colors = ['#8A4FFF', '#32B679', '#FF8C82', '#FFA726', '#4B7BF5']
        return colors[index % len(colors)]


# Create and customize the mind map
config = MindMapConfig(
    width=15,                         # Figure width in inches
    height=10,                        # Figure height in inches
    dpi=100,                          # Resolution
    x_limits=(-0.5, 11.5),            # X-axis limits
    y_limits=(-4.5, 4.5),             # Y-axis limits
    text_bar_height=0.3,              # Height of node bars
    text_padding=0.2,                 # Padding around text
    color_scheme=CustomColorScheme()  # Custom color scheme
)

# Create the mind map
mind_map = MindMap(config)
mind_map.create(mind_map_data)

# Save to file
mind_map.save("project_planning.png", bbox_inches='tight')

# Or display it
mind_map.show()
