"""
candl.lib module

Contains all necessary and optional imports
"""

# --------------------------------------#
# NECESSARY
# --------------------------------------#

import os

import inspect

from functools import partial

import importlib

import yaml
import logging

import numpy as np
import scipy as sp

from copy import deepcopy

import sigfig
from textwrap import wrap
from tqdm.notebook import tqdm

from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns

# --------------------------------------#
# OPTIONAL
# --------------------------------------#

# Optional JAX import
try:
    import jax.numpy as jnp
    import jax.scipy as jsp
    from jax import jit, jacfwd

    # Unify syntax for setting array elements
    def jax_optional_set_element(arr, ix, el):
        return arr.at[ix].set(el)

    # Need JAX to run with 64bit for dynamic range in covmats
    try:
        from jax.config import config

        config.update("jax_enable_x64", True)
    except:
        raise Exception(
            "candl: could not configure JAX to run in 64 bit mode - this will likely lead to wrong results!"
        )

except ImportError:
    import numpy as jnp
    import scipy as jsp

    # Unify syntax for setting array elements
    def jax_optional_set_element(arr, ix, el):
        arr[ix] = el
        return arr

    # define jit decorator to do nothing
    def jit(func, **kwargs):
        return func


# Optional pycapse import
try:
    import pycapse as pc
    import json
except:
    pass

# Optional CAMB import
try:
    import camb
except:
    pass

# Optional CLASS import
try:
    import classy
except:
    pass

# Optional Cobaya import
try:
    import cobaya.theory
except:
    pass

# Optional CosmoPower import
try:
    import cosmopower as cp
except:
    pass

# Optional CosmoPower-JAX import
try:
    from cosmopower_jax.cosmopower_jax import CosmoPowerJAX as CPJ
except:
    pass
