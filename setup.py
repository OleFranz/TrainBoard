from setuptools import setup

setup(
    name="TrainBoard",
    version="0.1",
    description="Track, visualize and log ML model training",
    author="OleFranz",
    license="GPL-3.0",
    packages=["TrainBoard"],
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "torch"
    ]
)