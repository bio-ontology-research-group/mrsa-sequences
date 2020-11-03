#!/usr/bin/env python3
import os
import sys

import setuptools.command.egg_info as egg_info_cmd
from setuptools import setup

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, "README.md")

try:
    import gittaggers

    tagger = gittaggers.EggInfoFromGit
except ImportError:
    tagger = egg_info_cmd.egg_info

install_requires = ["arvados-cwl-runner", "biopython", "rdflib<4.3.0", "pathlib2", "scandir", "Jinja2",
                    "python-magic", "pyshex<=0.7.14", "pyshexc<=0.7.0", "py-dateutil", "pyyaml", "click"]

needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest < 6", "pytest-runner < 5"] if needs_pytest else []

setup(
    name="mrsa-seq-uploader",
    version="1.0",
    description="MRSA sequence uploader",
    long_description=open(README).read(),
    long_description_content_type="text/markdown",
    author="Maxat Kulmanov",
    author_email="maxat.kulmanov@kaust.edu.sa",
    license="Apache 2.0",
    packages=["uploader", "analyzer"],
    package_data={"uploader": ["schema.yml",
                                "options.yml",
                                "shex.rdf",
                                "validation/formats"],
                "analyzer": ["report.py",
                                "report.html",
                                "menu.html"]
    },
    install_requires=install_requires,
    setup_requires=[] + pytest_runner,
    tests_require=["pytest<5"],
    entry_points={
        "console_scripts": [
            "mrsa-seq-uploader=uploader.main:main",
            "mrsa-seq-analyzer=analyzer.main:main"
        ]
    },
    zip_safe=True,
    cmdclass={"egg_info": tagger},
    python_requires=">=3.5, <4",
)
