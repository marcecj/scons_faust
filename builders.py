import os
import re

import SCons.Builder
import SCons.Defaults
import SCons.Scanner
import SCons.Script

FAUST = 'faust'
INCLUDE_RE = re.compile(r'import\s*\(\s*"([^"]+)"\s*\)\s*;', re.M)

def dsp_source_scanner(node, env, path):
    """Scan source files for imported files in `path'."""

    contents = node.get_contents()
    includes = INCLUDE_RE.findall(contents)
    path = [os.path.dirname(str(node))] + list(path)

    deps = filter(os.path.exists,
        [os.path.join(os.path.realpath(str(d)), f) for d in path for f in includes]
    )

    return deps

def dsp_target_scanner(node, env, path):
    """Search for architecture file in `path'."""

    arch = env['FAUST_ARCHITECTURE'] + '.cpp'
    return filter(os.path.exists, [os.path.join(str(d), arch) for d in path])

def svg_emitter(target, source, env):
    target = target + [os.path.join(str(t), 'process.svg') for t in target]
    print map(str, target)
    return (target, source)
    #return (target + [os.path.join(str(target[0]), 'process.svg')], source)

def svg_scanner(node, env, path):
    return [os.path.join(str(node), 'process.svg')]

dsp = SCons.Builder.Builder(
        action = 'faust ${FAUST_FLAGS} -a ${FAUST_ARCHITECTURE}.cpp -o $TARGET $SOURCE',
        suffix = '.cpp',
        src_suffix = '.dsp',
        target_scanner = Scons.Scanner.Scanner(
            function = dsp_target_scanner,
            path_function = SCons.Scanner.FindPathDirs('FAUST_PATH'))
)

xml = SCons.Builder.Builder(
        action = ['faust ${FAUST_FLAGS} -o /dev/null -xml $SOURCE', SCons.Defaults.Move('$TARGET', '${SOURCE}.xml')],
        suffix = '.dsp.xml',
        src_suffix = '.dsp'
)

svg = SCons.Builder.Builder(
        action = ['faust ${FAUST_FLAGS} -o /dev/null -svg $SOURCE', SCons.Defaults.Move('$TARGET', '${SOURCE}-svg')],
        suffix = '.dsp-svg',
        src_suffix = '.dsp',
        single_source = True,
        target_factory = SCons.Script.Dir,
        target_scanner = SCons.Scanner.Scanner(function = svg_scanner)
)

sc  = SCons.Builder.Builder(
        action = '$FAUST2SC --lang=sclang --prefix="${FAUST2SC_PREFIX}" -o $TARGET $SOURCES',
        suffix = '.sc',
        src_suffix = '.dsp.xml',
        multi = True
)

hs  = SCons.Builder.Builder(
        action = '$FAUST2SC --lang=haskell --prefix="${FAUST2SC_HASKELL_MODULE}" -o $TARGET $SOURCES',
        suffix = '.hs',
        src_suffix = '.dsp.xml',
        multi = True
)
