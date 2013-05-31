import os
import re

import SCons.Builder
import SCons.Scanner
import SCons.Script

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

    arch = env.subst('${FAUST_GET_ARCH}')
    return filter(os.path.exists, [os.path.join(str(d), arch) for d in path])

def svg_emitter(target, source, env):
    target = target + [os.path.join(str(t), 'process.svg') for t in target]
    print(map(str, target))
    return (target, source)
    #return (target + [os.path.join(str(target[0]), 'process.svg')], source)

dsp_src_scanner = SCons.Scanner.Scanner(
    function = dsp_source_scanner,
    recursive = True,
    path_function = SCons.Scanner.FindPathDirs('FAUST_PATH')
)

dsp_tgt_scanner = SCons.Scanner.Scanner(
    function = dsp_target_scanner,
    path_function = SCons.Scanner.FindPathDirs('FAUST_PATH')
)

faust_lang_suffix_map = {
    "cpp":  ".cpp",
    "c":    ".c",
    "java": ".jar",
    "js":   ".js",
    "llvm": ".ll",
    "fir":  ".fir", # TODO: not sure about this
}

faust_action = '$FAUST_FAUST \
${FAUST_FLAGS} \
${FAUST_VERSION >= "2" and "-lang $FAUST_LANG" or ""} \
-a ${FAUST_GET_ARCH} \
-o $TARGET $SOURCE'

dsp = SCons.Builder.Builder(
        action = faust_action,
        suffix = lambda env,srcs: faust_lang_suffix_map[env['FAUST_LANG']],
        src_suffix = '.dsp',
        source_scanner = dsp_src_scanner,
        target_scanner = dsp_tgt_scanner
)

xml = SCons.Builder.Builder(
        action = ['$FAUST_FAUST ${FAUST_FLAGS} -o /dev/null -xml $SOURCE',
                  SCons.Script.Move('$TARGET', '${SOURCE}.xml')],
        suffix = '.dsp.xml',
        src_suffix = '.dsp',
        source_scanner = dsp_src_scanner
)

svg = SCons.Builder.Builder(
        action = ['$FAUST_FAUST ${FAUST_FLAGS} -o /dev/null -svg $SOURCE',
                  SCons.Script.Move('$TARGET', '${SOURCE.filebase}-svg')],
        suffix = '.dsp-svg',
        src_suffix = '.dsp',
        single_source = True,
        source_scanner = dsp_src_scanner,
        target_factory = SCons.Script.Dir
)

sc  = SCons.Builder.Builder(
        action = '$FAUST2SC_FAUST2SC --lang=sclang --prefix="${FAUST2SC_PREFIX}" -o $TARGET $SOURCES',
        suffix = '.sc',
        src_suffix = '.dsp.xml',
        source_scanner = dsp_src_scanner,
        multi = True
)

hs  = SCons.Builder.Builder(
        action = '$FAUST2SC_FAUST2SC --lang=haskell --prefix="${FAUST2SC_HASKELL_MODULE}" -o $TARGET $SOURCES',
        suffix = '.hs',
        src_suffix = '.dsp.xml',
        source_scanner = dsp_src_scanner,
        multi = True
)
