# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging


def scale_memory(memory_limit, scaling_factor):
    """
    Return a scaled memory limit for batch jobs.

    Parameters
    ----------
    memory_limit : str
        Memory limit
    scaling_factor : float
        Scaling factor

    Returns
    -------
    : str
        Scaled memory limit. Note that the memory limit will be converted
        from GB to MB.
    """
    logger = logging.getLogger(__name__)
    # Note that slurm uses mebibyte and gebibytes for its limits
    memory_limit_mb = int(memory_limit[:-1]) * 1024
    scaled_memory_limit_mb = int(scaling_factor * memory_limit_mb)
    scaled_memory_limit = '{}M'.format(scaled_memory_limit_mb)

    logger.debug('Scaled memory limit from "{}" to "{}"'
                 ''.format(memory_limit, scaled_memory_limit))

    return scaled_memory_limit
