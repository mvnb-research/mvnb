from setuptools import find_packages, setup

packages = find_packages()

name = packages[0]

setup(
    name=name,
    packages=packages,
    entry_points=dict(
        console_scripts=[
            f"{name}-server={name}.server:main",
            f"{name}-console={name}.console:main",
        ]
    ),
    install_requires=[
        "bidict>=0.22.0,<0.23.0",
        "tornado>=6.2.0,<6.3.0",
    ],
)
