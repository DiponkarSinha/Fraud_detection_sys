from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fraud-detection-system",
    version="1.0.0",
    author="Fraud Detection Team",
    author_email="fraud-detection@company.com",
    description="Advanced Fraud Detection System with Machine Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diponkarsinha/Fraud_detection_sys",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
            "isort>=5.12",
        ],
        "aws": [
            "boto3>=1.28.0",
            "botocore>=1.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fraud-detect=src.api.main:main",
            "fraud-train=src.models.model_training:main",
            "fraud-data=src.data_processing.synthetic_data_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fraud_detection": ["config/*.json", "models/*.pkl"],
    },
)