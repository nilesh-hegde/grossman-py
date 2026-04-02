from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grossman",
    version="0.1.0",
    author="Nilesh Hegde",
    description="Python client for econometrics teaching datasets (grossman)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nilesh-hegde/grossman-py",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "pyreadr",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
    ],
)
