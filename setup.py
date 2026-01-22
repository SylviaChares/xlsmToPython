# setup.py
from setuptools import setup, find_packages

setup(
    name="barwerte",
    version="0.1.0",
    description="Versicherungsmathematische Barwertfunktionen",
    author="Sylvie",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',  # falls Sie Excel-Dateien lesen
    ],
    python_requires='>=3.11',
)