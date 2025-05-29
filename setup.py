"""
Setup script for the NeoServe AI package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("neoserve_ai/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neoserve-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="NeoServe AI - A multi-agent system for customer service and engagement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/neoserve-ai",
    packages=find_packages(include=["neoserve_ai", "neoserve_ai.*"]),
    package_data={
        "neoserve_ai": ["*.yaml", "*.json", "*.txt", "*.md"],
    },
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "neoserve-ai=neoserve_ai.cli:main",
        ],
    },
    extras_require={
        "dev": [
            line.strip()
            for line in open("neoserve_ai/requirements-dev.txt", "r", encoding="utf-8")
            if line.strip() and not line.startswith("#")
        ],
        "test": [
            "pytest>=7.3.1,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-httpx>=0.24.1,<1.0.0",
            "httpx>=0.24.1,<1.0.0",
        ],
    },
)
