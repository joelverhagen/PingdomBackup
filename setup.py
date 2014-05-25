import sys
import re
import setuptools

# detect the version, without an import
VERSION_FILE = 'pingdombackup/__init__.py'
version_contents = open(VERSION_FILE).read()
version_match = re.search(r'__version__\s*=\s*\'(.+?)\'', version_contents)
if version_match is None:
	__version__ = 'UNKNOWN'
else:
	__version__ = version_match.group(1)

setuptools.setup(
    name='PingdomBackup',
    version=__version__,
    description='Backup Pingdom logs',
    long_description='Backup Pingdom result logs to a SQLite database.',
    author='Joel Verhagen',
    author_email='joel.verhagen@gmail.com',
    install_requires=['requests>=2.1.0'],
    url='https://github.com/joelverhagen/PingdomBackup',
    packages=['pingdombackup'],
    license='MIT',
    entry_points=dict(console_scripts=['pingdombackup = pingdombackup:tool_main']),
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
