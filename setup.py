from setuptools import setup, find_packages
from sys import platform

# read the contents of the README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

platform_dependency_links = []
if platform.startswith('win'):
    print('Not installing QuickUMLS for Windows since it currently requires conda (as opposed to just pip)')
else:
    # Using a trick from StackOverflow to set an impossibly high version number
    # to force getting latest from GitHub as opposed to PyPi
    # since QuickUMLS has not made a release with some recent MedSpacy contributions...
    platform_dependency_links.append('https://github.com/Georgetown-IR-Lab/QuickUMLS/tarball/master#egg=999.0.0')

def get_version():
    """Load the version from version.py, without importing it.
    This function assumes that the last line in the file contains a variable defining the
    version string with single quotes.
    """
    try:
        with open('medspacy/_version.py', 'r') as f:
            return f.read().split('\n')[0].split('=')[-1].replace('\'', '').strip()
    except IOError:
        raise IOError

setup(
    name="medspacy",
    version=get_version(),
    description="Library for clinical NLP with spaCy.",
    author="medSpaCy",
    author_email="medspacy.dev@gmail.com",
    packages=find_packages(),
    install_requires=[
        # NOTE: spacy imports numpy to bootstrap its own setup.py in 2.3.2
        "spacy>=2.3.0,<=2.3.2",
        "PyRuSH>=1.0.3.5",
        "jsonschema"
    ],
    dependency_links = platform_dependency_links,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={"medspacy": ["../resources/*"]},
)
