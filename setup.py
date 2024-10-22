from setuptools import setup

setup(
    name='your-package-name',
    version='0.1',
    description='Your project description',
    packages=['your_package'],
    install_requires=[
        'fastapi',  # Example dependency
        'uvicorn'
    ],
)