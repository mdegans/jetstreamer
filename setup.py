import os
import setuptools

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(THIS_DIR, 'README.md')) as readme:
    long_description = readme.read()

setuptools.setup(
    name='jetstreamer',
    version='0.0.2',
    description='Image and inference metadata recording utility for NVIDIA Tegra',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',

        # TODO: add topics
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    # install_requires=[],
    packages=['jetstreamer'],
    entry_points={
        'console_scripts': ['jetstreamer=jetstreamer.__main__:cli_main']
    },
    author='Michael de Gans',
    project_urls={
        'Bug Reports': 'https://github.com/mdegans/jetstreamer/issues',
        'Source': 'https://github.com/mdegans/jetstreamer/',
    },
)
