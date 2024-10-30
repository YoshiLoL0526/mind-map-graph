from setuptools import setup, find_packages

setup(
    name="mindmap_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],
    author="Raidel Martínez Santos",
    author_email="yoshilol0526@gmail.com",
    description="A library for creating mind maps using Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yoshilol0526/mindmap_lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
