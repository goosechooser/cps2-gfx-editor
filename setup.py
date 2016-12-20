from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cps2-gfx-editor',
    version='0.0.1',
    description='toolset for editing cps2 tiles',
    long_description=readme,
    author='M B',
    author_email='dont@me',
    license=license,
    packages=['src'])

