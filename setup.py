import setuptools
import sys

if sys.platform == "win32":
    include_dirs = ["C:\\cibw\\vendor\\include"]
    library_dirs = ["C:\\cibw\\vendor\\lib"]
    libraries = ["libcrypto", "advapi32", "crypt32", "gdi32", "user32", "ws2_32"]
else:
    include_dirs = ["/tmp/vendor/include"]
    library_dirs = ["/tmp/vendor/lib"]
    libraries = ["crypto"]

setuptools.setup(
    name="dummy",
    package_dir={"": "src"},
    packages=["dummy"],
    ext_modules=[
        setuptools.Extension(
            "dummy.binding",
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            libraries=libraries,
            sources=["src/dummy/binding.c"],
        ),
    ],
)
