from setuptools import setup, find_packages

setup(
    name="eafsed",
    version="0.1",
    author="David Lukeš",
    author_email="dafydd.lukes@gmail.com",
    description="A sed for eaf files.",
    license="GNU GPLv3",
    url="https://github.com/dlukes/eafsed",
    packages=find_packages(),
    install_requires=[
        "click",
        "lxml",
        "regex",
    ],
    entry_points="""
        [console_scripts]
        eafsed=eafsed:main
    """,
)
