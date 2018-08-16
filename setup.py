from setuptools import setup, find_packages


setup(
    name='avs_client',
    version='0.7.1',
    packages=find_packages(exclude=["tests.*", "tests"]),
    url='https://github.com/richtier/alexa-voice-service-client',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python Client for Alexa Voice Service (AVS)',
    long_description=open('docs/README.rst').read(),
    include_package_data=True,
    install_requires=[
        'hyper>=0.7.0<1.0.0',
        'requests-toolbelt>=0.8.0<1.0.0',
        'requests>=2.19.1<3.0.0',
    ],
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
