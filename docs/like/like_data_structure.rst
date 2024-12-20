Data Structure
=================================================

Data sets are comprised of a set of text files and an info ``.yaml`` file.
The info file contains information about the data set, such as its name, the location of the data files, the data model, the priors, and any restriction of the data to be used.
If you are interested in understanding these in detail, we recommend looking at some of the released data sets as an example along with the explanations below.
You can also find more details in the :ref:`documentation<like_api>`.


Data Set Info File
-------------------------------------------------

The info file is a ``.yaml`` file containing the following information:

.. code-block:: yaml
   
      name: <name of data set>
      band_power_file: <relative path of the band power file>
      covariance_file: <relative path of the band power file>
      window_functions_folder: <relative path of the window functions folder>
      spectra_info:
         - <spectrum id>: <number of bins>
      data_model:
         - <transformation>
      priors:
         - <par_names>: <name of parameter to apply the prior to>
           <central_value>: <central value of the prior>
           <prior_std>: <width of the prior (standard deviation)>

The ``spectra_info`` block is a list of spectra in the likelihood specifying the order of spectra as well as their type, frequency, and number of bins; describing the data set accurately here is important.
The expected format for ``spectrum_id`` is:

* for primary CMB likelihoods: ``[spec] [id_1]x[id_2]``, where ``spec`` can be any of ``TT``, ``EE``, ``TE``, ``BB``, and ``id_1`` and ``id_2`` are string identifiers of the two maps, typically frequencies. Note that these only identifiers, not accurate band centres. For example: ``TT 90x150``.
* for lensing likelihoods : ``[spec]``, where ``spec`` is ``pp`` or ``kk``

These identifiers are then followed by the number of bins in the band power file for that spectrum.

The ``data_model`` block is a list of transformations to be applied to the data.
The transformations are applied in the order they are listed.
The entries for each block depend on the transformation to be used; they typically contain nuisance parameter names involved in the transformation and a list of spectra the transformation is applied to.
If no transformations are required, the ``data_model`` block can be omitted.

The ``priors`` block is a list of Gaussian priors to be applied to the cosmological or nuisance parameters.
Multidimensional Gaussian priors are also supported; in this case supply a list of strings for ``par_names``, a list of floats for ``central_value`` and the relative path of a the covariance with ``prior_covariance``, rather than using ``prior_std``.
Note that in this case, the order of the covariance is expected to match the order of names supplied in ``par_names``.
If no priors are required, the ``priors`` block can be omitted.

Effective Frequencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the likelihood requires effective frequencies to run, you can supply these via ``effective_frequencies: <relative path to the effective frequencies file>`` in the info file.
Effective frequencies are stored in a ``.yaml`` file with the following format:

.. code-block:: yaml
   
   <source keyword>:
     <frequency identifier>: <effective frequency>

For example, the source keyword may be ``cirrus``, the frequency identifier ``150``, and the effective frequency ``150.1``.

Other entries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Along with the entries described above, the info file can contain the following other entries:

* ``feedback: <True/False>``: whether to print feedback when initialising the likelihood. Helps to review the data selection and data model.
* ``log_file: <relative path to log file>``: forego printing of feedback in favour of writing to a log file.
* ``beam_correlation_file: <relative path to beam correlation matrix>``: beam correlation matrix (if needed).
* ``likelihood_form: <gaussian/gaussian_beam_detcov>``: alternative form of the likelihood if correction for beam covariance matrix is required (default: ``gaussian``).
* ``bandpasses: <dictionary of frequency identifiers and band pass file names>``: needed if integrals over band passes are required for any transformations (typically only for :math:`BB`).
* ``blinding: <True/False/int>``: whether to blind the band powers (through multiplication by a random oscillatory function). Integers are used as seeds.
* ``hartlap_correction: <dictionary with 'N_sims' entry>``: will apply the `Hartlap factor <https://arxiv.org/abs/astro-ph/0608064>`__ to the inverse covariance matrix.

.. note::

    Instead of modifying the ``.yaml`` file to tweak these options, you can also pass these keywords when initialising the likelihood object.
    Anything passed during initialisation will override the options in the yaml file.

Data Files
-------------------------------------------------

The band power and covariance files are text files containing the band powers and covariance matrix for the data set.
The order and length of spectra must match what is declared under ``spectra_info`` in the info file.
The covariance is in 'spectrum-major' order, i.e. all bins of spectrum #1, all bins of spectrum #2, etc.

The window functions start at :math:`\ell=2` and can be stored in the ``window_functions_folder`` in two ways:

#. As ``[spec]_window_functions.txt`` files, where ``spec`` is the spectrum identifier with underscores replacing spaces, e.g. ``TT_150x150_window_functions.txt``. The files are arrays of (ell, N_bins+1) size, where the first column gives the theory ell.
#. As ``window_[i].txt`` starting at ``i=0``. The files are arrays of (ell, N_specs+1) size, where the first column gives the theory ell.

The first format is preferred as it allows for spectra of different length.

Band passes are text files containing of two columns: the frequency and the response to a uniform source at that frequency, normalised to unity at the peak.

M matrices for lensing likelihoods are stored as ``window_[i].txt`` files (starting at ``i=0``) in a separate folder, i.e. matching the second format option for band power window functions above.
Each file is expected to contain six columns in the following order: ell, :math:`TT`, :math:`TE`, :math:`EE`, :math:`BB`, :math:`\phi\phi/\kappa\kappa`.

Index Files
-------------------------------------------------

Index files contain the file names of different variants of the same likelihood in a dictionary format.
Index files are optional, you can always initiate likelihoods by pointing directly towards the desired data set info ``.yaml`` file.
However, they can help you navigate between different variants without cluttering your working space.
For example, they are handy when switching between the versions of lensing likelihoods used when performing analyses with or without primary CMB data.
If you find yourself making lots of variations of a data set info file, consider linking between them with an index file.
Index files are ``.yaml`` files with the following format:

.. code-block:: yaml
   
      default: <data set info file>
      a_variant: <data set info file>
      another_variant: <data set info file>
