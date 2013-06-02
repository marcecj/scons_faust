"""SCons.Tool.faust

Tool for building faust dsp files.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import os
import SCons.Errors

def _gen_faust_architecture(target, source, env, for_signature):

    has_ext   = os.path.splitext(env['FAUST_ARCHITECTURE'])[1] != ''
    arch_file = env['FAUST_ARCHITECTURE'] + ('' if has_ext else '.cpp')

    return arch_file

def _get_prog_path(env, key, name):
    """Try to find the executable 'name' and store its location in env[key]."""

    # check if the user already specified the location
    try:
        return env[key]
    except KeyError:
        pass

    # on windows faust might be named faust.exe
    prog_path = env.WhereIs(name) or env.WhereIs(name+'.exe')

    if not prog_path:
        raise SCons.Errors.EnvironmentError("faust not found")

    return prog_path

def generate(env):

    import subprocess as subp
    from . import builders

    env.Append(BUILDERS = { 'Faust':        builders.dsp,
                            'FaustXML':     builders.xml,
                            'FaustSVG':     builders.svg,
                            'FaustSC':      builders.sc,
                            'FaustHaskell': builders.hs })

    faust_faust = _get_prog_path(env, 'FAUST_FAUST', 'faust')
    faust2sc    = _get_prog_path(env, 'FAUST2SC_FAUST2SC', 'faust2sc')

    try:
        faust_proc = subp.Popen([faust_faust, '--version'], stdout=subp.PIPE)
        faust_ver = faust_proc.communicate()[0].splitlines()[0].split()[-1]
    except Exception as e:
        print("Error getting faust version: " + str(e))
        faust_ver = ''

    try:
        faust2sc_proc = subp.Popen([faust2sc, '--version'], stdout=subp.PIPE)
        faust2sc_ver = faust2sc_proc.communicate()[0].split()[-1]
    except Exception as e:
        print("Error getting faust2sc version: " + str(e))
        faust2sc_ver = ''


    env.SetDefault(
        # set faust defaults
        FAUST_FAUST              = faust_faust,
        FAUST_VERSION            = faust_ver,
        FAUST_LANG               = 'cpp',
        FAUST_ARCHITECTURE       = 'module',
        FAUST_FLAGS              = SCons.Util.CLVar(''),
        FAUST_PATH               = SCons.Util.CLVar(
            ['.', '/usr/local/lib/faust', '/usr/lib/faust']
        ),

        # set faust2c defaults
        FAUST2SC_FAUST2SC         = faust2sc,
        FAUST2SC_VERSION         = faust2sc_ver,
        FAUST2SC_PREFIX          = '',
        FAUST2SC_HASKELL_MODULE  = '',

        # private variables
        FAUST_GET_ARCH           = _gen_faust_architecture
    )

def exists(env):
    # expect faust2sc to be there if faust is
    return _get_prog_path(env, 'FAUST_FAUST', 'faust')
