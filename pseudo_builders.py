import os
import SCons.Errors
from . import builders

def svg_builder(env, target, source, *args, **kwargs):
    """
    A pseudo-builder for generating SVGs via faust -svg.

    In addition to what the SVG builder does, this pseudo-builder marks the SVG
    directory for cleaning.
    """

    r = builders.svg(env, target, source, *args, **kwargs)

    # make sure to clean up the directory with the SVG files
    for t in r:
        env.Clean(t, t.abspath)

    return r

def doc_builder(env, target, source, *args, **kwargs):
    """
    A pseudo-builder for generating documentation via faust -mdoc.

    In addition to what the doc builder does, this pseudo-builder marks the mdoc
    directory for cleaning.
    """

    source = [env.File(s) for s in source]
    r = builders.doc(env, target, source, *args, **kwargs)

    s_basename = os.path.splitext(os.path.basename(source[0].path))[0]

    # get a bunch of paths
    top_dir  = env.Dir(r.pop(0).abspath)
    svg_dir  = top_dir.Dir("svg")
    svg_dir0 = svg_dir.Dir("svg-01")
    tex_dir  = top_dir.Dir("tex")
    pdf_dir  = top_dir.Dir("pdf")

    process_svg = svg_dir0.File("process.svg")
    process_pdf = svg_dir0.File("process.pdf")
    tex_path    = tex_dir.File(s_basename+".tex")
    pdf_path    = pdf_dir.File(s_basename+".pdf")

    # compile the LaTeX sources to PDF
    process_pdf = env.SVG2PDF(process_pdf, process_svg)
    mdoc_pdf    = env.PDF(pdf_path, tex_path)

    # the svg and pdf subdirectories change because of process_pdf and
    # mdoc_pdf, so make sure the *-mdoc directory ignores them
    env.Ignore(top_dir,  [svg_dir, tex_dir, pdf_dir])
    env.Ignore(svg_dir0, process_pdf)
    env.Ignore(pdf_dir,  mdoc_pdf)

    # set the dependencies straight
    env.Depends([process_svg, tex_path], top_dir)
    env.Depends(mdoc_pdf, process_pdf)

    r.extend([mdoc_pdf, process_pdf])

    # make sure to clean up the documentation directory
    env.Clean(r, top_dir.abspath)

    return r

def dsp_builder(env, target, source, *args, **kwargs):
    """
    A pseudo builder for compiling FAUST DSPs.

    In addition to what the DSP builder does, this pseudo-builder checks the
    FAUST version and raises an error when FAUST_LANG is not "cpp" and
    FAUST_VERSION is lower than 2.
    """

    if env['FAUST_VERSION'] < "2" and env['FAUST_LANG'] != "cpp":
        raise SCons.Errors.UserError(
            "FAUST 1 does not support languages other than C++."
        )

    return builders.dsp(env, target, source, *args, **kwargs)
