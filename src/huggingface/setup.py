import sys
from pathlib import Path

import setuptools

readme = Path("README.md")
if readme.exists():
    long_description = (Path("README.md")).read_text()
else:
    long_description = (
        "Provide Forte implementations of a fantastic collection of NLP tools."
    )

if sys.version_info < (3, 6):
    sys.exit("Python>=3.6 is required by Forte.")

setuptools.setup(
    name="forte.huggingface",
    version="0.0.3",
    url="https://github.com/asyml/forte-wrappers/tree/main/src/huggingface",
    description="Provide Forte implementations of a fantastic collection of "
    "NLP tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License Version 2.0",
    packages=["fortex.huggingface"],
    namespace_packages=["fortex"],
    include_package_data=True,
    platforms="any",
    install_requires=[
        "forte==0.2.0",
        "more-itertools>=8.0.0",
        "transformers == 4.2.2",
        "numpy == 1.19.5",
        "sentencepiece>=0.1.96",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
