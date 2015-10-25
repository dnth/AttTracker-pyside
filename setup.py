from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = ['collections.abc'], include_files = ['pics/', 'python.jpg', 'unknown_profile.png'] )

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base)
]

setup(
    name='AttTracker',
    version = '0.1',
    description = 'A PyQt Attendance Program',
    options = dict(build_exe = buildOptions),
    executables = executables
)