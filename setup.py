from setuptools import find_packages, setup
from re import search, M

VERSIONFILE = 'mikud/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = search(version_re, version_line, M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(
    name='mikud',
    packages=find_packages(),
    version=version,
    description="Get mikud (zip code in israel) by address.",
    long_description=(open('README.rst', encoding='utf-8').read()),
    long_description_content_type="text/x-rst",
    author_email='davidlev@telegmail.com',
    url='https://mikud.readthedocs.io',
    author='David Lev',
    license='MIT',
    install_requires=['requests'],
)
