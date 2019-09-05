from setuptools import setup
from setuptools import find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='knowledge-hiic',
    version='0.1',
    author='Benjamin Brownlee',
    author_email='benjamin.brownlee1@gmail.com',
    description='scripts for generating and manipulation HII-C knowledge source',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HII-C/Knowledge',
    packages=find_packages(where='scripts'),
    package_dir={"": "scripts"},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)