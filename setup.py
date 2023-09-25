import json

def load_dependencies_from_pipfile_lock():
    with open("Pipfile.lock", "r") as f:
        lock_content = json.load(f)
        default_packages = {pkg: details['version'] for pkg, details in lock_content["default"].items()}
        develop_packages = {pkg: details['version'] for pkg, details in lock_content["develop"].items()}
        return default_packages, develop_packages

default_requires, dev_requires = load_dependencies_from_pipfile_lock()

# Convert the dictionaries into list of strings with pinned versions
install_requires = [f"{pkg}{version}" for pkg, version in default_requires.items()]
dev_requires = [f"{pkg}{version}" for pkg, version in dev_requires.items()]


from setuptools import setup, find_packages

setup(
    name="NASTI",
    version="0.4.0",
    description="NASTI's A Strange Templating Implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adamrdrew/nasti",
    author="Adam Drew",
    author_email="adamrdrew@live.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "nasti=nasti.cli:cli",
        ],
    },
)