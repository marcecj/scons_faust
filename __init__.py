"""SCons.Tool.faust

Tool for building faust dsp files.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

#
# Copyright (c) 2008 Stefan Kersten
# Copyright (c) 2013 Marc Joliet
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

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

    from . import builders

    env.Append(BUILDERS = { 'Faust'         : builders.dsp,
                            'FaustXML'      : builders.xml,
                            'FaustSVG'      : builders.svg,
                            'FaustSC'       : builders.sc,
                            'FaustHaskell'  : builders.hs })

    env['FAUST_FAUST']              = _get_prog_path(env, 'FAUST_FAUST', 'faust')
    env['FAUST_ARCHITECTURE']       = 'module'
    env['FAUST_FLAGS']              = []
    env['FAUST_PATH']               = ['.', '/usr/local/lib/faust', '/usr/lib/faust']
    env['FAUST2SC']                 = _get_prog_path(env, 'FAUST_FAUST2C', 'faust2c')
    env['FAUST2SC_PREFIX']          = ''
    env['FAUST2SC_HASKELL_MODULE']  = ''

    # private variables
    env['FAUST_GET_ARCH']           = _gen_faust_architecture

def exists(env):
    # expect faust2sc to be there if faust is
    return _get_prog_path(env, 'FAUST_FAUST', 'faust')
