set destdir=%1
set outputfile=output\openssl-win%PYTHON_ARCH%.tar.gz

for %%d in (openssl %destdir%) do (
    if exist %%d (
        rmdir /s /q %%d
    )
)

if %PYTHON_ARCH% == 64 (
   set OPENSSL_CONFIG=VC-WIN64A
   set VC_ARCH=x64
) else (
   set OPENSSL_CONFIG=VC-WIN32
   set VC_ARCH=x86
)

call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" %VC_ARCH%
SET PATH=%PATH%;C:\Program Files\NASM

mkdir openssl
curl -L https://www.openssl.org/source/openssl-1.1.1i.tar.gz -o openssl.tar.gz
tar xzf openssl.tar.gz -C openssl --strip-components 1
cd openssl

perl Configure no-comp no-shared no-tests %OPENSSL_CONFIG%
nmake

mkdir %destdir%
mkdir %destdir%\include
mkdir %destdir%\lib
xcopy include %destdir%\include\ /E
copy libcrypto.lib %destdir%\lib\
copy libssl.lib %destdir%\lib\
cd ..

if not exist output (
    mkdir output
)
SET PATH=C:\Program Files\Git\usr\bin;%PATH%
tar czvf %outputfile% -C %destdir% include lib
dir output
