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
