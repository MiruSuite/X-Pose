@echo off
setlocal

set "PROJECT_ROOT=%~dp0.."

for /f "usebackq tokens=1,* delims==" %%A in ("%PROJECT_ROOT%\.env") do set "%%A=%%B"

if not exist "%CUDA_HOME%\bin\nvcc.exe" (
    echo nvcc.exe was not found under CUDA_HOME: %CUDA_HOME%
    exit /b 1
)

if not exist "%XPOSE_VSDEVCMD_BAT%" (
    echo Visual Studio developer command was not found: %XPOSE_VSDEVCMD_BAT%
    exit /b 1
)

call "%XPOSE_VSDEVCMD_BAT%" -arch=%VSCMD_ARG_TGT_ARCH% -host_arch=x64
if errorlevel 1 exit /b %errorlevel%

set "CUDA_PATH=%CUDA_HOME%"
set "PATH=%CUDA_HOME%\bin;%XPOSE_WINSDK_BIN%;%PATH%"
set "MAX_JOBS=1"

if not exist "%XPOSE_WINSDK_BIN%\rc.exe" (
    echo rc.exe was not found under XPOSE_WINSDK_BIN: %XPOSE_WINSDK_BIN%
    exit /b 1
)

for /f "delims=" %%C in ('where cl.exe') do (
    set "CC=%%C"
    set "CXX=%%C"
    goto found_cl
)

echo cl.exe was not found after loading the Visual Studio developer environment.
exit /b 1

:found_cl

cd /d "%PROJECT_ROOT%\models\UniPose\ops"
"%PROJECT_ROOT%\.venv39\Scripts\python.exe" setup.py build install
