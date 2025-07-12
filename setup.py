from setuptools import setup, find_packages

setup(
    name="cmov",
    version="0.1.0",
    description="Composable video animation engine",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=[
        "Pillow",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    url="https://github.com/yourusername/cmov",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
