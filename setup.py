from pathlib import Path
from setuptools import setup, find_packages

root = Path(__file__).parent
readme = (root / "README.md")
if readme.exists():
    long_desc = readme.read_text(encoding="utf-8")
    long_desc_type = "text/markdown"
else:
    long_desc = "Generate Markdown docs from GitHub Action action.yml files."
    long_desc_type = "text/plain"

setup(
    name="cifolio",
    version="0.3.0",
    description="Generate Markdown docs from GitHub Action action.yml files",
    long_description=long_desc,
    long_description_content_type=long_desc_type,
    author="",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "PyYAML>=6.0",
        "ollama>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "cifolio=action_teller.cli:cli",
        ],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
    ],
)
