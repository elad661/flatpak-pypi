from setuptools import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='flatpak-pypi',
      version='0.1.0',
      packages=['flatpak_pypi'],
      install_requires=requirements,
      entry_points={'console_scripts': ['flatpak-pypi = flatpak_pypi.__main__:main']})
