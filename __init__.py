"""SCons.Tool.faust

Tool for building faust dsp files.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import os
import SCons.Errors

def _gen_faust_architecture(target, source, env, for_signature):
    """
    Generate a valid FAUST architecture file name from FAUST_ARCHITECTURE and
    FAUST_LANG.
    """

    from . builders import faust_lang_suffix_map

    arch_fname, ext = os.path.splitext(env['FAUST_ARCHITECTURE'])

    # if the architecture file was specified without a suffix, default to the
    # suffix corresponding to the selected $FAUST_LANG
    if ext == '':
        ext = faust_lang_suffix_map[env['FAUST_LANG']]

    return arch_fname + ext

def _get_prog_path(env, key, name):
    """Try to find the executable 'name' and store its location in env[key]."""

    # check if the user already specified the location
    try:
        return env[key]
    except KeyError:
        pass

    # on windows faust might be named faust.exe
    prog_path = env.WhereIs(name) or env.WhereIs(name+'.exe')

    # Explicitly do not raise an error here. If FAUST is not installed, then the
    # build system using this tool should be able to deal with it.
    return prog_path

def generate(env):

    import subprocess as subp
    from . import builders
    from . import pseudo_builders

    env.Append(BUILDERS = { 'Faust':        pseudo_builders.dsp_builder,
                            'FaustXML':     builders.xml,
                            'FaustSVG':     pseudo_builders.svg_builder,
                            'FaustMDoc':    pseudo_builders.doc_builder,
                            'FaustSC':      builders.sc,
                            'FaustHaskell': builders.hs })

    faust_faust = _get_prog_path(env, 'FAUST_FAUST', 'faust')
    faust2sc    = _get_prog_path(env, 'FAUST2SC_FAUST2SC', 'faust2sc')

    try:
        assert faust_faust != None, "faust not available"
        faust_proc = subp.Popen([faust_faust, '--version'], stdout=subp.PIPE)
        faust_ver = faust_proc.communicate()[0].splitlines()[0].split()[-1]
    except Exception as e:
        print("Error getting faust version: " + str(e))
        faust_ver = ''

    try:
        assert faust2sc != None, "faust2sc not available"
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

        # set faust2sc defaults
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
