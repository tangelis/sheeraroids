from setuptools import setup

setup(
    name="sheera-vs-tux",
    version="1.0.0",
    description="A game where Sheera uses sound waves to defend against Tux penguins",
    author="Sheera Fan",
    author_email="sheera@example.com",
    url="https://github.com/yourusername/sheera-vs-tux",
    py_modules=["linux_asteroids"],
    install_requires=[
        "pygame>=2.1.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Arcade",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)