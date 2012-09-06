# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa

setup(
    name='pecan-wtforms',
    version='0.1.0a',
    description="""
    """,
    long_description=None,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
    keywords='',
    url='',
    author='Ryan Petrello',
    author_email='ryan (at) ryanpetrello.com',
    license='MIT',
    install_requires=['pecan', 'wtforms'],
    tests_require=['WebTest >= 1.3.1'],  # py3 compat
    test_suite='pecan_wtforms.tests',
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [pecan.extension]
    wtforms = pecan_wtforms
    """
)
