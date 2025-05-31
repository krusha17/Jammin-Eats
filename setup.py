from setuptools import setup, find_packages

setup(
    name="jammin_eats",
    version="0.5.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame>=2.0.0",
        "pytmx>=3.31"
    ],
    author="Krusha17",
    author_email="example@example.com",
    description="A food truck game with retro vibes",
    keywords="game, pygame, food truck",
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'jammin-eats=main:main',
        ],
    },
)
