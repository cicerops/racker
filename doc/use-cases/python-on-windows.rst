###############################
Use cases for Python on Windows
###############################


*************************
Build wheels for PyTables
*************************

DIY, without a hosted CI provider.

References
==========

- https://github.com/PyTables/PyTables/pull/872#issuecomment-773535041
- https://github.com/PyTables/PyTables/blob/master/.github/workflows/wheels.yml

Synopsis
========

.. note::

    The ``windows-pytables-wheel.sh`` program is part of this repository. You
    will only find it at the designated location when running ``racker`` from
    the working tree of its Git repository.

    You still can get hold of the program and invoke it, by downloading it from
    `windows-pytables-wheel.sh`_.

So, let's start by defining the download URL to that file::

    export PAYLOAD_URL=https://raw.githubusercontent.com/cicerops/racker/windows/doc/use-cases/windows-pytables-wheel.sh

Unattended::

    time racker --verbose run --rm --platform=windows/amd64 python:3.9 -- \
        "sh -c 'wget ${PAYLOAD_URL}; sh windows-pytables-wheel.sh'"

Or, interactively::

    racker --verbose run -it --rm --platform=windows/amd64 python:3.9 -- bash
    wget ${PAYLOAD_URL}
    sh windows-pytables-wheel.sh


Future
======

See https://github.com/cicerops/racker/issues/8.

When working on the code base, you can invoke the program directly from
the repository, after the ``--volume`` option got implemented::

    # Unattended.
    time racker --verbose run --rm \
        --volume=C:/Users/amo/dev/cicerops-foss/sources/postroj:C:/racker \
        --platform=windows/amd64 python:3.9 -- \
        sh /c/racker/doc/use-cases/windows-pytables-wheel.sh

    # Interactively.
    racker --verbose run -it --rm \
        --volume=C:/Users/amo/dev/cicerops-foss/sources/postroj:C:/racker \
        --platform=windows/amd64 python:3.9 -- bash
    /c/racker/doc/use-cases/windows-pytables-wheel.sh


.. _windows-pytables-wheel.sh: https://raw.githubusercontent.com/cicerops/racker/main/doc/use-cases/windows-pytables-wheel.sh
