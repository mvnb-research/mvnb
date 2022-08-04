from setuptools import find_packages, setup

packages = find_packages()

name = packages[0]

setup(
    name=name,
    packages=packages,
    entry_points=dict(
        console_scripts=[
            f"{name}={name}.__main__:main",
        ]
    ),
    install_requires=[
        "bidict>=0.22.0,<0.23.0",
        "prompt-toolkit>=3.0.0,<3.1.0",
        "tornado>=6.2.0,<6.3.0",
    ],
)
