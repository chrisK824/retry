from setuptools import setup, find_packages

setup(
    name="retry-reloaded",
    version="0.0.4",
    description="A simple Python library for retrying functions \
        with various backoff and callback strategies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chrisK824/retry",
    author="Chris Karvouniaris",
    author_email="christos.karvouniaris247@gmail.com",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    python_requires=">=3.7",
    license_files=["LICENSE"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
