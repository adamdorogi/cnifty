from setuptools import setup, find_packages

setup(
    name='cnifty',
    version='0.1.0',
    description='Create and launch NFT collections on Cardano.',
    long_description='',
    url='',
    author='',
    author_email='',
    license='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'cnifty=cnifty.cnifty:cli',
        ],
    },
)
