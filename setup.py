from setuptools import setup, find_packages

setup(
    name="sheeraroids",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame>=2.1.0",
        "numpy>=1.20.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "sheeraroids=linux_asteroids:main",
        ],
    },
    python_requires=">=3.6",
    author="Sheeraroids Team",
    description="A game where Sheera uses sound waves to defend against Iguanas",
    keywords="game, pygame, asteroids",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Arcade",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)