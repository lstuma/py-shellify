from setuptools import setup, find_packages

try:
    with open("README.md", "r") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="py-shellify",
    version="0.1.0",
    license="MIT",
    packages=find_packages(),
    description="Improved shell scripting using Python!",
    long_description=long_description,
    install_requires=[
        "psutil",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "pysh=pyshell.__main__:main",
            "pysh-run=pyshell.__main__:run",
            "pysh-new=pyshell.__main__:new",
            "pysh-switch=pyshell.__main__:switch",
            "pysh-close=pyshell.__main__:close",
        ]
    }
)
