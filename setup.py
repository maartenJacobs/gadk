import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gadk",
    version="0.0.1",
    author="Maarten Jacobs",
    author_email="maarten.j.jacobs@gmail.com",
    description="Unofficial Github Actions Development Kit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maartenJacobs/gadk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
