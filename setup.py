from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tool-combo-chains",
    version="0.1.0",
    author="Jordan Ehrig",
    author_email="jordan@ebicinc.com",
    description="Cognitive Amplification Stack - PostgreSQL hybrid memory with vector embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SamuraiBuddha/tool-combo-chains",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=0.1.0",
        "asyncpg>=0.29.0",  # Async PostgreSQL
        "redis>=5.0.0",     # Redis client
        "qdrant-client>=1.7.0",  # Qdrant vector DB
        "httpx>=0.25.0",    # For embedding API calls
        "pydantic>=2.0.0",  # Data validation
        "python-dotenv>=1.0.0",  # Environment variables
        "numpy>=1.24.0",    # Vector operations
        "structlog>=24.0.0",  # Structured logging
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "hybrid-memory=tool_combo_chains.mcp_hybrid_memory:main",
            "pattern-analyzer=tool_combo_chains.mcp_pattern_analyzer:main",
        ],
    },
)
