# The Climate Data Dissemination System (CDDS)

The Climate Data Dissemination System (CDDS) is a Python-based system that manages the reprocessing of HadGEM3 and UKESM1 climate model data into a standards compliant ([CMOR](https://cmor.llnl.gov/)) form suitable for publication and sharing. The primary driver behind CDDS was the CMIP6 project and CDDS was used, and is continuing to be used, to deliver a large amount of data to the [Centre for Environmental Data Archival (CEDA)](http://www.ceda.ac.uk) for publication to ESGF. 

CDDS has recently been adapted to allow for the easy addition of both models and projects, provided that they follow the structure for CMIP6, i.e. via predefined activities (MIPS), source ids (models) and experiments. As of version 2.2.4 CDDS supports production of data for CMIP6 and for a Met Office internal project [GCModelDev](https://github.com/MetOffice/gcmodeldev-cmor-tables) where Met Office scientists are encouraged to request additional activities and experiments that can be used to support their science. Note that the GCModelDev project is not intended to prepare data for publication -- anyone wanting to publish data or prepare it for an external project is encouraged to contact the [CDDS team](mailto:cdds@metoffice.gov.uk) or start a discussion here.

[The wiki](../../wiki) has further details and links
