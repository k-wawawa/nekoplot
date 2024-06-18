from setuptools import setup, find_packages

NAME = 'nekoplot'
__version__ = '0.1.0'

setup(
    name=NAME,
    version=__version__,
    author='Kei Watanabe',
    author_email='jasri.kei.watanabe@gmail.com',
    description='plotting with wxPython and skia',
    install_requires=[
        'wxPython',
        'skia-python',
        'opencv-python',
        'numpy'
    ],
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={"":"src"},
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    python_requires=">=3.9"
)