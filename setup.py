import os, sys

from setuptools import setup, Extension

import shutil

from subprocess import check_output as subprocess_check_output

from setuptools.command.build_ext import build_ext

VERSION = "2.13.1"

def check_output(popenargs):
    print("(running '%s')" % (" ".join(popenargs)))
    return subprocess_check_output(popenargs)


ICU_MAX_MAJOR_VERSION = "76"  # max supported major version of ICU


def configure_with_icu_config(flags, config_args, label):
    try:
        output = check_output(("icu-config",) + config_args).strip()
        if sys.version_info >= (3,):
            output = str(output, "ascii")
        flags.extend(output.split())
        if output:
            print(
                'Adding %s="%s" from %s' % (label, output, shutil.which("icu-config"))
            )
    except:
        print("Could not configure %s with icu-config" % (label))
        raise


def configure_with_pkg_config(flags, config_args, label):
    try:
        output = check_output(("pkg-config",) + config_args + ("icu-i18n",)).strip()
        if sys.version_info >= (3,):
            output = str(output, "ascii")
        flags.extend(output.split())
        if output:
            print(
                'Adding %s="%s" from %s' % (label, output, shutil.which("pkg-config"))
            )
    except:
        print("Could not configure %s with pkg-config" % (label))
        raise


platform = sys.platform
if platform.startswith(("linux", "gnu")):
    platform = "linux"
elif platform.startswith("freebsd"):
    platform = "freebsd"

CONFIGURE_WITH_ICU_CONFIG = {
    "darwin": False,
    "linux": True,
    "freebsd": False,  # not tested
    "win32": False,  # no icu-config
    "sunos5": False,  # not tested
}

CONFIGURE_WITH_PKG_CONFIG = {
    "darwin": False,  # no pkg-config ?
    "linux": True,
    "freebsd": False,  # not tested
    "win32": False,  # no pkg-config ?
    "sunos5": False,  # not tested
}

os.environ['ICU_VERSION'] = '76.1'

if 'ICU_VERSION' in os.environ:
    ICU_VERSION = os.environ["ICU_VERSION"]
else:
    try:
        ICU_VERSION = check_output(("icu-config", "--version")).strip()
        CONFIGURE_WITH_ICU_CONFIG[platform] = True
    except:
        try:
            ICU_VERSION = check_output(
                ("pkg-config", "--modversion", "icu-i18n")
            ).strip()
            CONFIGURE_WITH_PKG_CONFIG[platform] = True
        except:
            raise RuntimeError(
                """
Please install pkg-config on your system or set the ICU_VERSION environment
variable to the version of ICU you have installed.
        """
            )
    ICU_VERSION = str(ICU_VERSION, "ascii")

print(
    """
Building PyICU %s for ICU %s (max ICU major version supported: %s)
"""
    % (VERSION, ICU_VERSION, ICU_MAX_MAJOR_VERSION)
)

INCLUDES = {
    "darwin": [],
    "linux": [
        '/usr/local/include',  # cibuildwheel
    ],
    "freebsd": ["/usr/local/include"],
    "win32": ["./vendor/icu/icu4c/source/common"],
    "sunos5": [],
    "cygwin": [],
}

if sys.platform == "win32" and sys.version_info < (3, 9):
    ver_flag = '/D%s=\\"%s\\"'
else:
    ver_flag = '-D%s="%s"'

VER_FLAGS = [
    ver_flag % ("PYICU_VER", VERSION),
    ver_flag % ("PYICU_ICU_MAX_VER", ICU_MAX_MAJOR_VERSION),
]

# added to CFLAGS when setup is invoked with --pedantic
PEDANTIC_FLAGS = {
    "darwin": ["-pedantic"],
    "linux": ["-pedantic", "-Wno-variadic-macros"],
    "freebsd": ["-pedantic"],
    "win32": [],
    "sunos5": [],
    "cygwin": ["-pedantic"],
}

CFLAGS = {
    "darwin": ["-std=c++17"],
    "linux": ["-std=c++17"],
    "freebsd": ["-std=c++17"],
    "win32": ["/Zc:wchar_t", "/EHsc"],
    "sunos5": ["-std=c++17"],
    "cygwin": ["-D_GNU_SOURCE=1", "-std=c++17"],
}

# added to CFLAGS when setup is invoked with --debug
DEBUG_CFLAGS = {
    "darwin": ["-O0", "-g", "-DDEBUG"],
    "linux": ["-O0", "-g", "-DDEBUG"],
    "freebsd": ["-O0", "-g", "-DDEBUG"],
    "win32": ["/Od", "/DDEBUG"],
    "sunos5": ["-DDEBUG"],
    "cygwin": ["-Og", "-g", "-DDEBUG"],
}

LFLAGS = {
    "darwin": [],
    "linux": [],
    "freebsd": ["-L/usr/local/lib"],
    "win32": ["/LIBPATH:.\\vendor\\icu\\icu4c\\lib64"],
    "sunos5": [],
    "cygwin": [],
}

LIBRARIES = {
    "darwin": [],
    "linux": [],
    "freebsd": ["icui18n", "icuuc", "icudata"],
    "win32": ["icuin", "icuuc", "icudt"],
    "sunos5": ["icui18n", "icuuc", "icudata"],
    "cygwin": ["icui18n", "icuuc", "icudata"],
}

if "PYICU_INCLUDES" in os.environ:
    _includes = os.environ["PYICU_INCLUDES"].split(os.pathsep)
else:
    _includes = INCLUDES[platform]

if "PYICU_CFLAGS" in os.environ:
    _cflags = os.environ["PYICU_CFLAGS"].split(os.pathsep)
else:
    _cflags = CFLAGS[platform]

if "--debug" in sys.argv:
    sys.argv.remove("--debug")
    if "PYICU_DEBUG_CFLAGS" in os.environ:
        _cflags += os.environ["PYICU_DEBUG_CFLAGS"].split(os.pathsep)
    else:
        _cflags += DEBUG_CFLAGS[platform]

if "--pedantic" in sys.argv:
    sys.argv.remove("--pedantic")
    _cflags += PEDANTIC_FLAGS[platform]

_cflags += VER_FLAGS

if "PYICU_LFLAGS" in os.environ:
    _lflags = os.environ["PYICU_LFLAGS"].split(os.pathsep)
else:
    # if platform == "linux":
    # _lflags = ['-L/usr/local/lib', '-licui18n', '-licuuc','-licudata']
    # else:
    _lflags = LFLAGS[platform]
    if CONFIGURE_WITH_ICU_CONFIG[platform]:
        try:
            configure_with_icu_config(_lflags, ("--ldflags",), "LFLAGS")
        except:
            if CONFIGURE_WITH_PKG_CONFIG[platform]:
                configure_with_pkg_config(_lflags, ("--libs",), "LFLAGS")
            else:
                raise
    elif CONFIGURE_WITH_PKG_CONFIG[platform]:
        configure_with_pkg_config(_lflags, ("--libs",), "LFLAGS")

if "PYICU_LIBRARIES" in os.environ:
    _libraries = os.environ["PYICU_LIBRARIES"].split(os.pathsep)
else:
    _libraries = LIBRARIES[platform]

print(dict(
    include_dirs=_includes,
    extra_compile_args=_cflags,
    extra_link_args=_lflags,
    libraries=_libraries,
))

setup(
    name="PyICU",
    description="Python extension wrapping the ICU C++ API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://gitlab.pyicu.org/main/pyicu",
    author="Andi Vajda",
    author_email="vajda@pyicu.org",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Localization",
        "Topic :: Software Development :: Internationalization",
    ],
    ext_modules=[
        Extension(
            "icu._icu_",
            [
                filename
                for filename in sorted(os.listdir(os.curdir))
                if filename.endswith(".cpp")
            ],
            include_dirs=_includes,
            extra_compile_args=_cflags,
            extra_link_args=_lflags,
            libraries=_libraries,
        )
    ],
    cmdclass={"build_ext": build_ext},
    package_dir={"": "py"},
    packages=["icu"],
)
