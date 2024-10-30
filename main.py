import json

from mindmap_lib import MindMap
from mindmap_lib.core import MindMapConfig
from mindmap_lib.rendering import EnhancedGradientScheme


def create_sample_json():
    """
    Crea un ejemplo de datos de mapa mental en formato JSON.
    Este ejemplo representa un resumen sobre Python.
    """
    mind_map_data = {
        "text": "Python",
        "children": [
            {
                "text": "Core Features",
                "children": [
                    {
                        "text": "Data Types",
                        "children": [
                            {"text": "Numbers", "children": [
                                {"text": "Integer", "children": []},
                                {"text": "Float", "children": []}
                            ]},
                            {"text": "Strings", "children": []},
                            {"text": "Data Structures", "children": [
                                {"text": "Lists", "children": []},
                                {"text": "Dictionaries", "children": []},
                                {"text": "Sets", "children": []},
                                {"text": "Tuples", "children": []}
                            ]}
                        ],
                    },
                    {
                        "text": "Control Flow",
                        "children": [
                            {"text": "Conditions", "children": [
                                {"text": "if", "children": []},
                                {"text": "elif", "children": []},
                                {"text": "else", "children": []},
                            ]},
                            {"text": "Cycles", "children": [
                                {"text": "for loops", "children": []},
                                {"text": "while loops", "children": []}
                            ]},
                            {"text": "Exception handling", "children": [
                                {"text": "try/except", "children": []},
                            ]},
                        ]
                    },
                    {
                        "text": "Functions",
                        "children": [
                            {"text": "def keyword", "children": []},
                            {"text": "lambda", "children": []},
                            {"text": "arguments", "children": [
                                {"text": "*args", "children": []},
                                {"text": "**kwargs", "children": []},
                            ]},
                            {"text": "return values", "children": []},
                        ],
                    },
                ],
            },
            {
                "text": "Advanced Topics",
                "children": [
                    {
                        "text": "OOP",
                        "children": [
                            {"text": "Classes", "children": []},
                            {"text": "Inheritance", "children": []},
                            {"text": "Polymorphism", "children": []},
                            {"text": "Encapsulation", "children": []},
                        ],
                    },
                    {
                        "text": "Modules",
                        "children": [
                            {"text": "import", "children": []},
                            {"text": "packages", "children": []},
                            {"text": "pip", "children": []},
                        ],
                    },
                ],
            },
            {
                "text": "Libraries",
                "children": [
                    {
                        "text": "Data Science",
                        "children": [
                            {"text": "NumPy", "children": []},
                            {"text": "Pandas", "children": []},
                            {"text": "Matplotlib", "children": []},
                        ],
                    },
                    {
                        "text": "Web",
                        "children": [
                            {"text": "Django", "children": []},
                            {"text": "Flask", "children": []},
                            {"text": "FastAPI", "children": []},
                        ],
                    },
                    {
                        "text": "Digital image processing",
                        "children": [
                            {"text": "OpenCV", "children": []}
                        ],
                    },
                ],
            },
        ],
    }
    return json.dumps(mind_map_data, indent=2)


def create_custom_config():
    """
    Crea una configuración personalizada para el mapa mental.
    """
    return MindMapConfig(
        width=24,                                   # Ancho mayor para más espacio
        height=14,                                  # Alto mayor para más espacio
        dpi=120,                                    # Mayor DPI para mejor resolución
        x_limits=(-1.5, 22.5),                      # Límites X ajustados al nuevo ancho
        y_limits=(-6, 6),                           # Límites Y ajustados al nuevo alto
        text_bar_height=0.35,                       # Barras de texto más altas
        text_padding=0.25,                          # Más padding para el texto
        color_scheme=EnhancedGradientScheme(),      # Esquema de color personalizado
    )


def main():
    """
    Función principal que demuestra diferentes formas de crear y personalizar
    mapas mentales.
    """
    # 1. Crear el JSON con los datos
    json_data = create_sample_json()

    # 2. Crear mapa mental con configuración personalizada
    custom_mindmap = MindMap(config=create_custom_config())
    custom_mindmap.create_from_json(json_data)

    # 3. Guardar mapa mental resultante
    custom_mindmap.save(
        "example.png", bbox_inches="tight", pad_inches=0.1, dpi=150
    )

    # 4. Mostrar mapa mental interactivamente
    custom_mindmap.show()


if __name__ == "__main__":
    main()
