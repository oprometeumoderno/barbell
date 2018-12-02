import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='barbell',
    version='0.2.1',
    scripts=['barbell'],
    author="Henrique de Paula",
    author_email="oprometeumoderno@gmail.com",
    description="A tool for creating Gym environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/oprometeumoderno/barbell",
    packages=setuptools.find_packages(),
    install_requires=['gym', 'stringcase'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
