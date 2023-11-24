import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

    setuptools.setup(
        name="mtsat",
        version="0.0.3",
        author="Oleksii Pshenychnyi",
        author_email="afw@afw.net.ua",
        description="Mikrotik routers control script for Nodeny",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/pshenyaga/mtsat",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3.6",
            "License :: OSI Approved :: GNU GPLv3",
            "Operating System :: OS Independent"
        ],
        install_requires=[
            'mtapi @ git+https://github.com/pshenyaga/mtapi#egg=mtapi-0.0.1'
        ],
    )
