from setuptools import setup, find_packages


setup(
    name='alexa_client',
    version='1.5.0',
    packages=find_packages(exclude=["tests.*", "tests"]),
    url='https://github.com/richtier/alexa-voice-service-client',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python Client for Alexa Voice Service (AVS)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'hyper>=0.7.0<1.0.0',
        'requests-toolbelt>=0.8.0<1.0.0',
        'requests>=2.19.1<3.0.0',
        'resettabletimer>=0.6.3,<1.0.0',
    ],
    extras_require={
        'test': [
            'flake8==3.4.0',
            'freezegun==0.3.9',
            'pytest-cov==2.5.1',
            'pytest-sugar==0.9.0',
            'pytest==3.2.0',
            'requests_mock==1.3.0',
            'codecov==2.0.9',
            'twine>=1.11.0,<2.0.0',
            'wheel>=0.31.0,<1.0.0',
            'setuptools>=38.6.0,<39.0.0',
        ],
        'demo': [
            'pydub>=0.23.0,<1.0.0',
            'pyaudio>=0.2.11,<1.0.0',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
