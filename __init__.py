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

def generate(env):

    from builders import *

    env.Append(BUILDERS = { 'Faust'         : dsp,
                            'FaustXML'      : xml,
                            'FaustSVG'      : svg,
                            'FaustSC'       : sc,
                            'FaustHaskell'  : hs })

    env['FAUST_ARCHITECTURE']       = 'module'
    env['FAUST_FLAGS']              = []
    env['FAUST_PATH']               = ['.', '/usr/local/lib/faust', '/usr/lib/faust']
    env['FAUST2SC']                 = 'faust2sc'
    env['FAUST2SC_PREFIX']          = ''
    env['FAUST2SC_HASKELL_MODULE']  = ''
    
    env.Append(SCANNERS = [
        env.Scanner(function = dsp_source_scanner,
                    skeys = ['.dsp'],
                    path_function = SCons.Scanner.FindPathDirs('FAUST_PATH'))
        ])

def exists(env):
    return (env.WhereIs(FAUST) or SCons.Util.WhereIs(FAUST))
