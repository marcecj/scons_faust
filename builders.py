import os
import re

import SCons.Builder
import SCons.Scanner
import SCons.Script

###################
# the DSP builder #
###################

INCLUDE_RE = re.compile(r'import\s*\(\s*"([^"]+)"\s*\)\s*;', re.M)

def dsp_source_scanner(node, env, path):
    """Scan source files for imported files in `path'."""

    contents = node.get_contents()
    includes = [env.File(i) for i in INCLUDE_RE.findall(contents)]
    path     = [node.Dir('.').path] + list(path)

    deps = [env.FindFile(str(f), path) for f in includes]

    return deps

def dsp_target_scanner(node, env, path):
    """Search for architecture file in `path'."""

    arch = env.subst('${FAUST_GET_ARCH}')
    return [env.FindFile(arch, path)]

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

###################
# the XML builder #
###################

xml = SCons.Builder.Builder(
    action = ['$FAUST_FAUST ${FAUST_FLAGS} -o /dev/null -xml $SOURCE',
              SCons.Script.Move('$TARGET', '${SOURCE}.xml')],
    suffix = '.dsp.xml',
    src_suffix = '.dsp',
    single_source = True,
    source_scanner = dsp_src_scanner
)

###################
# the SVG builder #
###################

svg = SCons.Builder.Builder(
    action = ['$FAUST_FAUST ${FAUST_FLAGS} -o /dev/null -svg $SOURCE',
              SCons.Script.Move('$TARGET', '${SOURCE.base}-svg')],
    suffix = lambda env,srcs: "-svg",
    src_suffix = '.dsp',
    single_source = True,
    source_scanner = dsp_src_scanner,
    target_factory = SCons.Script.Dir
)

#############################
# the documentation builder #
#############################

def doc_emitter(target, source, env):

    orig_t = env.Dir(target[0])

    # only return directories with static content
    target = [orig_t.Dir(d) for d in ("cpp", "src")]

    return target, source

cairosvg = SCons.Builder.Builder(
    action = 'cairosvg --format=pdf -o $TARGET $SOURCE',
    suffix = '.pdf',
    src_suffix = '.svg',
    single_source = True
)

doc_action_list = [
    '$FAUST_FAUST ${FAUST_FLAGS} -o /dev/null -mdoc $SOURCE',
    # NOTE: apparently the first Move() creates the directory without actually
    # executing the move, so a Mkdir() is needed first
    SCons.Script.Mkdir('${TARGET.dir}'),
    [SCons.Script.Move('${TARGET.dir}',
                       '${SOURCE.base}-mdoc'+os.sep+subdir)
     for subdir in ("src", "cpp", "svg", "tex", "pdf")],
    SCons.Script.Delete('${SOURCE.base}-mdoc')
]

doc = SCons.Builder.Builder(
    action = SCons.Script.Flatten(doc_action_list),
    suffix = lambda env,srcs: "-mdoc",
    src_suffix = '.dsp',
    single_source = True,
    source_scanner = dsp_src_scanner,
    target_factory = SCons.Script.Dir,
    emitter = doc_emitter
)

##############################
# the supercollider builders #
##############################

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
