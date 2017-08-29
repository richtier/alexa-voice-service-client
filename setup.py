from setuptools import setup, find_packages

import pip.download
from pip.req import parse_requirements


def get_requirements():
    requirements = parse_requirements(
        'requirements.txt',
        session=pip.download.PipSession()
    )
    return [str(r.req) for r in list(requirements)]


setup(
    name='avs_client',
    version='0.5.1',
    packages=find_packages(exclude=["tests.*", "tests"]),
    url='https://github.com/richtier/alexa-voice-service-client',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python Client for Alexa Voice Service (AVS)',
    long_description=open('README.rst').read(),
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
