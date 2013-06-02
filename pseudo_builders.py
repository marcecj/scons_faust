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
        env.Clean(t, t.path)

    return r
