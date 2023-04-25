from setuptools import setup, find_packages

setup(
    name="opcua-server-benchmark",
    version="0.1",
    install_requires=[
        "numpy",
        "pandas",
        "tqdm",
        "pyaml",
        "asyncua",
        "click",
        "matplotlib",
    ],
    packages=find_packages(),
)
