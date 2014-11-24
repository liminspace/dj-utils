# coding=utf-8
import os
from distutils.core import setup
from setuptools import find_packages
import dj_utils


setup(
    name='dj-utils',
    version=dj_utils.__version__,
    description='Django utilities.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read(),
    license='BSD',
    author='liminspace',
    author_email='liminspace@gmail.com',
    url='https://github.com/liminspace/dj-utils',
    packages=find_packages(),  # exclude=('tests.*', 'tests', 'example')
    include_package_data=True,
    zip_safe=False,  # тому, що вкладаємо статику
    requires=[
        'django',
        'simplejson'
    ],
)
