# -*- coding: utf-8 -*-
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

setup(
    name="racker",
    version="0.2.0",
    author="Andreas Motl",
    author_email="andreas.motl@cicerops.de",
    url="https://github.com/cicerops/racker",
    description="Racker is an experimental harness tool for provisioning and launching operating system containers",
    long_description=README,
    download_url="https://pypi.org/project/racker/",
    packages=["racker", "postroj"],
    license="AGPL-3.0, EUPL-1.2",
    keywords=[
        "systemd",
        "systemd-nspawn",
        "systemd-container",
        "systemd-run",
        "machinectl",
        "virtual",
        "environment",
        "build",
        "test",
        "testing",
        "test-harness",
        "harness-framework",
        "test-environment",
        "testing-tool",
        "harness",
        "oci",
        "oci-image",
        "oci-images",
        "virtualbox",
        "vagrant",
        "docker",
        "docker-image",
        "skopeo",
        "umoci",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Emulators",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "racker = racker.cli:cli",
            "postroj = postroj.cli:cli",
        ],
    },
    install_requires=[
        "appdirs>=1,<2",
        "click>=7,<9",
        "furl>=2,<3",
        "subprocess-tee>=0.3,<1",
        "python-slugify>=6,<7",
        "tld>=0.10,<1",
    ],
    extras_require={
        "test": [
            "pytest>=6,<8",
            "pytest-cov>=2,<3",
            "re-assert>=1,<2",
        ]
    },
)
