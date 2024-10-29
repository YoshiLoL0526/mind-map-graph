import matplotlib.pyplot as plt

from mind_map import MindMap

plt.switch_backend('TkAgg')


def main():
    # Definimos los datos del mapa mental
    mind_map_data = (
        "Programación",
        [
            ("Frontend", [
                ("HTML", []),
                ("CSS", []),
                ("JavaScript", [])
            ]),
            ("Backend", [
                ("Python", []),
                ("Bases de Datos", [
                    ("SQL", []),
                    ("NoSQL", [])
                ]),
                ("DevOps", [])
            ]),
            ("Herramientas", [
                ("Control de Versiones", [
                    ("Git", []),
                    ("Mercurial", []),
                    ("Subversion", [])
                ]),
                ("Testing", []),
                ("Editores", [])
            ])
        ]
    )

    # Create and show mind map
    mind_map = MindMap()
    mind_map.create(mind_map_data)
    mind_map.show()


if __name__ == "__main__":
    main()
