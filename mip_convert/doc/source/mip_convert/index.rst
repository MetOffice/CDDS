.. Copyright (C) British Crown (Met Office) & Contributors.
.. Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
.. See the LICENSE file in the top level of this repository for full details.

*********
Reference
*********
.. toctree::
   :maxdepth: 1

   process/model_to_mip_mappings.rst
   process/processors.rst
   process/constants.rst


*****
Notes
*****

MIP Convert does make some alterations to the PP header of PP files when loading them. 
The changes are currently determined by entries in the `cdds.common.constants.PP_HEADER_CORRECTIONS` dictionary.