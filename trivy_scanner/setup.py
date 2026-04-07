"""
Setup script for Trivy Vulnerability Scanner Dashboard
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trivy-scanner-dashboard",
    version="1.0.0",
    author="Sarvani Shriyan",
    author_email="sarvanishriyan@gmail.com",
    description="A comprehensive web dashboard for visualizing Trivy container vulnerability scan results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sarvanishriyan-lgtm/Trivy-Scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "trivy-dashboard=trivy_scanner.app.app:app.run",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)