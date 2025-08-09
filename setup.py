from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kafka-ai-agent",
    version="0.1.0",
    author="Kafka AI Agent Contributors",
    description="Intelligent Kafka Schema Registry Management with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aywengo/kafka-ai-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "mcp>=0.1.0",
        "anthropic>=0.18.0",
        "openai>=1.12.0",
        "google-generativeai>=0.3.0",
        "confluent-kafka>=2.3.0",
        "requests>=2.31.0",
        "avro-python3>=1.10.0",
        "jsonschema>=4.20.0",
        "protobuf>=4.25.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "prometheus-client>=0.19.0",
        "structlog>=24.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kafka-ai-agent=kafka_ai_agent:main",
        ],
    },
)