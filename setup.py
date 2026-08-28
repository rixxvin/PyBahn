from setuptools import setup, find_packages

setup(
    name='PyBahn',
    version='0.1.17',
    packages=find_packages(),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "httpx",
        "reportlab",
        "pydantic"
    ]
)