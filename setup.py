import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="AutoPypline",
    version="1.0.0",
    author="Sumukha Manjunath",
    author_email="sumukha1996@gmail.com",
    description="A package for automating python pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sumukha21/AutoPypline",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)