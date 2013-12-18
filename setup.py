import sys
from setuptools import setup

setup(
    name='pingdombackup',
    version='0.1.0',
    description='Backup Pingdom logs',
    long_description='Backup Pingdom result logs to a SQLite database.',
    author='Joel Verhagen',
    author_email='joel.verhagen@gmail.com',
    install_requires=['requests>=2.1.0'],
    url='https://github.com/joelverhagen/PingdomBackup',
    packages=['pingdombackup'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 3',
    ]
)
