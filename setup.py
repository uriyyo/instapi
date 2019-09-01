from pathlib import Path

from setuptools import (
    find_packages,
    setup,
)

__version__ = '0.0.1'

README: Path = Path(__file__).parent / 'README.md'

setup(
    name='instapi',
    version=__version__,
    python_requires='>=3.6',
    author='Yurii Karabas',
    author_email='1998uriyyo@gmail.com',
    url='https://github.com/uriyyo/instapi',
    include_package_data=True,
    description="InstAPI - comfortable and easy to use Python's library for interaction with Instagram",
    long_description=README.read_text(),
    license='MIT',
    packages=find_packages(exclude=('tests*',)),
    install_requires=[
        'dataclasses==0.6.0',
        'instagram-private-api==1.6.0.0',
        'Pillow==6.1.0',
        'requests==2.22.0',
    ],
    extras_require={
        'testing': [
            'pytest==5.1.2',
            'pytest-mock==1.10.4',
            'pytest-cov==2.7.1',
            'mypy==0.720',
        ],
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
