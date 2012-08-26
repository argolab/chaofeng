#!/usr/bin/python2

'''
A simple telnet bbs server framework for python.
'''

from setuptools import setup

setup(name='chaofeng',
      version='0.09',
      description='A simple telnet bbs server framework for python.',
      author='LTaoist',
      author_email='LTaoist6@gmail.com',
      url='https://github.com/LTaoist/chaofeng',
      packages=['chaofeng'],
      install_requires=['eventlet'],
      )
