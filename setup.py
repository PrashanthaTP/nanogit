from setuptools import setup

setup(name='nanogit', version='0.1.0', packages=['nanogit'],entry_points = {'console_scripts':['ngit = nanogit.cli:main']})
