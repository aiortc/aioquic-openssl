import os
import platform
import shutil
import struct
import subprocess
import sys

if len(sys.argv) < 2:
    sys.stderr.write("Usage: build-openssl.py <prefix>\n")
    sys.exit(1)

dest_dir = sys.argv[1]
build_dir = os.path.abspath("build")
patch_dir = os.path.abspath("patches")
source_dir = os.path.abspath("source")

for d in [build_dir, dest_dir]:
    if os.path.exists(d):
        shutil.rmtree(d)


def get_platform():
    system = platform.system()
    machine = platform.machine()
    if system == "Linux":
        if platform.libc_ver()[0] == "glibc":
            return f"manylinux_{machine}"
        else:
            return f"musllinux_{machine}"
    elif system == "Darwin":
        return f"macosx_{machine}"
    elif system == "Windows":
        if struct.calcsize("P") * 8 == 64:
            return "win_amd64"
        else:
            return "win32"
    else:
        raise Exception(f"Unsupported system {system}")


def extract(package, url, *, strip_components=1):
    path = os.path.join(build_dir, package)
    patch = os.path.join(patch_dir, package + ".patch")
    tarball = os.path.join(source_dir, url.split("/")[-1])

    # download tarball
    if not os.path.exists(tarball):
        run(["curl", "-L", "-o", tarball, url])

    # extract tarball
    os.mkdir(path)
    run(["tar", "xf", tarball, "-C", path, "--strip-components", str(strip_components)])

    # apply patch
    if os.path.exists(patch):
        run(["patch", "-d", path, "-i", patch, "-p1"])


def run(cmd, *, env=None):
    sys.stdout.write(f"- Running: {cmd}\n")
    subprocess.run(
        cmd, check=True, env=env, stderr=sys.stderr.buffer, stdout=sys.stdout.buffer
    )


configure_args = []
output_dir = os.path.abspath("output")
if platform.system() == "Linux" and os.environ.get("CIBUILDWHEEL") == "1":
    output_dir = "/output"
    try:
        run(["yum", "-y", "install", "perl-IPC-Cmd"])
    except Exception:
        # Alpine Linux doesn't use yum.
        pass
output_tarball = os.path.join(output_dir, f"openssl-{get_platform()}.tar.gz")

for d in [build_dir, output_dir, source_dir]:
    if not os.path.exists(d):
        os.mkdir(d)
if not os.path.exists(output_tarball):
    os.chdir(build_dir)

    # build openssl
    extract("openssl", "https://www.openssl.org/source/openssl-3.4.1.tar.gz")
    os.chdir("openssl")
    run(["./config"] + configure_args + ["no-apps", "no-comp", "no-dso", "no-shared", "no-tests"])
    run(["make"])
    run(["make", "install_sw", "INSTALLTOP=" + dest_dir, "LIBDIR=lib"])

    run(["tar", "czvf", output_tarball, "-C", dest_dir, "include", "lib"])
