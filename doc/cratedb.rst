#######################################
Using Racker and Postroj for CrateDB CI
#######################################


**********
racker run
**********

Purpose: Invoke programs in a Java/OpenJDK environment, within a
virtualized/dockerized, volatile/ephemeral Windows environment.

Run the CrateDB test suite on OpenJDK 18 (Eclipse Temurin)::

    time racker --verbose run --rm --platform=windows/amd64 eclipse-temurin:18-jdk \
        "sh -c 'mkdir /c/src; cd /c/src; git clone https://github.com/crate/crate --depth=1; cd crate; ./gradlew --no-daemon --parallel -PtestForks=2 :server:test -Dtests.crate.run-windows-incompatible=false --stacktrace'"

Use the same image, but select a specific operating system version::

    export RACKER_WDM_MACHINE=2019-box
    racker --verbose run --rm --platform=windows/amd64 eclipse-temurin:18-jdk -- wmic os get caption

Invoke a Java command prompt (JShell) with OpenJDK 18::

    racker --verbose run -it --rm --platform=windows/amd64 eclipse-temurin:18-jdk jshell
    System.out.println("OS: " + System.getProperty("os.name") + ", version " + System.getProperty("os.version"))
    System.out.println("Java: " + System.getProperty("java.vendor") + ", version " + System.getProperty("java.version"))


****************
postroj pkgprobe
****************

Purpose: Test distribution packages.

Test package on Debian bullseye::

    postroj pkgprobe \
        --image=debian-bullseye \
        --package=https://cdn.crate.io/downloads/apt/testing/pool/main/c/crate/crate_4.7.2-1~bullseye_amd64.deb \
        --check-unit=crate \
        --check-network=http://localhost:4200 \
        --check-network=tcp://localhost:5432 \
        --network-timeout=30

Test package on Fedora 36::

    postroj pkgprobe \
        --image=fedora-36 \
        --package=https://cdn.crate.io/downloads/yum/testing/7/x86_64/crate-4.7.2-1.x86_64.rpm \
        --check-unit=crate \
        --check-network=http://localhost:4200 \
        --check-network=tcp://localhost:5432 \
        --network-timeout=30

.. todo::

    Probing the HTTP port 4200 of CrateDB currently still responds with::

        HTTP/1.1 503 Service Unavailable

    Improve!
