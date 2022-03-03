import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="sone",
    version="1.1.2",
    author="Hotte Shen",
    author_email="hotteshen@gmail.com",
    description="iHealth Sauna Controller App",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hotteshen/eastec.s1",
    project_urls={
        "Bug Tracker": "https://github.com/hotteshen/eastec.s1/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["sone"],
    include_package_data = True,
    python_requires=">=3.6",
    install_requires=required,
)
