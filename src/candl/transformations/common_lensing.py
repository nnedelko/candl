"""
candl.transformations.common_lensing module

Common transformations for lensing likelihoods.

Note: the transformations of lensing likelihoods act on binned spectra.

Warning: this is NOT a comprehensive foreground/data model library. Instead, the classes below are designed
for the data sets implemented in candl and serve as examples that you can use to implement any model you want.

Transformations:
--------
BinnedTemplateForeground
ResponseFunctionM
LensingAmplitude
"""

# --------------------------------------#
# IMPORTS
# --------------------------------------#

from candl.lib import *
import candl.transformations.abstract_base

# --------------------------------------#
# LENSING TRANSFORMATIONS
# --------------------------------------#


class BinnedTemplateForeground(candl.transformations.abstract_base.Foreground):
    """
    Template foreground that is already binned, with a single amplitude parameter.

    Methods
    ---------
    __init__ :
        initialises an instance of the class.
    output :
        gives the additive foreground contribution.
    transform :
        transforms an input spectrum.

    Attributes
    -------
    template_arr : array (float)
        Template spectrum and ells.
    template_spec : array (float)
        Template spectrum.
    template_ells : array (int)
        Template ells.
    ells : array (float)
        The ell range the transformation acts on.
    descriptor : str
        A short descriptor.
    par_names : list
        Names of parameters involved in transformation.
    amp_param : str
        The name of the amplitude parameter.
    """

    def __init__(self, ells, template_arr, amp_param, descriptor=""):
        """
        Initialise a new instance of the BinnedTemplateForeground class.

        Arguments
        -------
        ells : array (float)
            The ell range the transformation acts on.
        descriptor : str
            A short descriptor.
        amp_param : str
            The name of the amplitude parameter.
        template_arr : array (float)
            Array with two columns, the first for ell values, the second for values of the template spectrum.

        Returns
        -------
        Foreground
            A new instance of the BinnedTemplateForeground class.
        """

        super().__init__(ells=ells, descriptor=descriptor, param_names=[amp_param])

        # Read in template
        self.template_arr = template_arr
        self.template_spec = self.template_arr[:, 1]
        self.template_ells = self.template_arr[:, 0]

        # Grab other args
        self.ells = ells
        self.amp_param = amp_param

    def output(self, sample_params):
        """
        Return foreground spectrum.
        Intended to be overwritten by subclasses.

        Arguments
        -------
        sampled_params : dict
            Dictionary of nuisance parameter values.

        Returns
        -------
        array, float
            Foreground spectrum.
        """

        return self.template_spec * sample_params[self.amp_param]

    def transform(self, Dls, sample_params):
        """
        Transform spectrum by adding foreground component (result of output method).
        Intended to be overwritten by subclasses.

        Arguments
        -------
        Dls : array
            Dls to transform.
        sampled_params : dict
            Dictionary of nuisance parameter values.

        Returns
        -------
        array, float
            Transformed spectrum.
        """

        return Dls + self.output(sample_params)


class ResponseFunctionM(candl.transformations.abstract_base.Transformation):
    """
    Calculates M * (Cth) - M * (Cfid)

    Methods
    ---------
    __init__ :
        initialises an instance of the class.
    output :
        gives the additive contribution.
    transform :
        Returns a transformed spectrum.

    Attributes
    -------
    ells : array (float)
        The ell range the transformation acts on.
    descriptor : str
        A short descriptor.
    M_matrix : array (float)
        The matrix of the transformation.

    """

    def __init__(self, ells, M_matrices, fiducial_correction, descriptor=""):
        """
        Initialise the ResponseFunctionM transformation.

        Arguments
        -------
        ells : array (float)
            The ell range the transformation acts on.
        descriptor : str
            A short descriptor.
        M_matrices : dictionary of array (float)
            A dictionary with the matrix(es) of the transformation.
        fiducial_correction : array (float)
            An array with the fiducial correction (M * C_fid) values.

        Returns
        -------
        Transformation
            A new instance of the ResponseFunctionM class.
        """

        super().__init__(ells=ells, descriptor=descriptor)
        self.M_matrices = M_matrices
        self.fiducial_correction = fiducial_correction

    @partial(jit, static_argnums=(0,))
    def output(self, sample_params):
        """
        Return the correction.
        Needs to use unbinned (from params) spectra.

        Arguments
        -------
        sample_params dict
            Contains the unbinned (pp, TT) theory spectra to be used in calculating (M * C).

        Returns
        -------
        array, float
            Response function contribution.
        """

        # M * (Cth) - M * (Cfid)

        # get required modes and fiducial correction
        M_modes = self.M_matrices.keys()
        M_correction = -self.fiducial_correction

        # multiply arrays according to length of theory spectra
        l_length = len(jnp.block(sample_params["Dl"]["pp"]))

        for mode in M_modes:
            M_correction += jnp.dot(
                np.transpose(self.M_matrices[mode][:l_length]),
                jnp.block(sample_params["Dl"][mode]),
            )
        return M_correction

    @partial(jit, static_argnums=(0,))
    def transform(self, Dls, sample_params):
        """
        Transform the input spectrum.

        Arguments
        -------
        Dictionary of Dls : dict of array (float)
            The binned spectra (pp) to add to (M * C).
        sample_params dict
            Contains the unbinned (pp, TT) theory spectra to be used in calculating (M * C).

        Returns
        -------
        array : float
            Response function contribution.
        """

        return Dls + self.output(sample_params)


class LensingAmplitude(candl.transformations.abstract_base.Transformation):
    """
    Lensing amplitude function, which multiplies the input by an overall constant.

    Methods
    ---------
    __init__ :
        initialises an instance of the class.
    output :
        amp_param.
    transform :
        transforms an input spectrum as amp_param * input.

    Attributes
    -------
    ells : array (float)
        The ell range the transformation acts on.
    descriptor : str
        A short descriptor.
    par_names : list
        Names of parameters involved in transformation.
    amp_param : str
        The name of the amplitude parameter.
    """

    def __init__(self, ells, amp_param, descriptor=""):
        """
        Initialise a new instance of the LensingAmplitude class.

        Arguments
        -------
        ells : array (float)
            The ell range the transformation acts on.
        descriptor : str
            A short descriptor.
        amp_param : str
            The name of the amplitude parameter.

        Returns
        -------
        Foreground
            A new instance of the LensingAmplitude class.
        """

        super().__init__(ells=ells, descriptor=descriptor, param_names=[amp_param])

        # Grab other args
        self.ells = ells
        self.amp_param = amp_param

    def output(self, sample_params):
        """
        Return multiplicative factor.
        Intended to be overwritten by subclasses.

        Arguments
        -------
        sampled_params : dict
            Dictionary of nuisance parameter values.

        Returns
        -------
        float
            Multiplicative factor.
        """

        return sample_params[self.amp_param]

    def transform(self, Dls, sample_params):
        """
        Transform spectrum by multiplying by overall constant factor (result of output method).
        Intended to be overwritten by subclasses.

        Arguments
        -------
        Dls : array
            Dls to transform.
        sampled_params : dict
            Dictionary of nuisance parameter values.

        Returns
        -------
        array, float
            Transformed spectrum.
        """

        return Dls * self.output(sample_params)
