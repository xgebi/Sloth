import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slothcms",
    version="0.0.121",
    author="Sarah Gebauer",
    author_email="sarah@sarahgebauer.com",
    description="Sloth Content Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xgebi/Sloth",
    package_dir={'sloth': 'src/cms'},
    packages=['sloth'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Hippocratic License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)