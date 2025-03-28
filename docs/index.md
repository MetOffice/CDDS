# Climate Data Dissemination System

The Climate Data Dissemination System (CDDS) is a Python-based system that manages the reprocessing of HadGEM3 and UKESM1 climate model data into a standards compliant ([CMOR](https://cmor.llnl.gov/)) form suitable for publication and sharing. The primary driver behind CDDS was the CMIP6 project and CDDS was used, and is continuing to be used, to deliver a large amount of data to the [Centre for Environmental Data Archival (CEDA)](http://www.ceda.ac.uk) for publication to ESGF. 

CDDS has recently been adapted to allow for the easy addition of both models and projects, provided that they follow the structure for CMIP6, i.e. via predefined activities (MIPS), source ids (models) and experiments. As of version 2.2.4 CDDS supports production of data for CMIP6 and for a Met Office internal project [GCModelDev](https://github.com/MetOffice/gcmodeldev-cmor-tables) where Met Office scientists are encouraged to request additional activities and experiments that can be used to support their science. Note that the GCModelDev project is not intended to prepare data for publication -- anyone wanting to publish data or prepare it for an external project is encouraged to contact the [CDDS team](mailto:cdds@metoffice.gov.uk) or start a discussion here.

## Contact

You can contact the CDDS team via cdds@metoffice.gov.uk.

## CMIP6 Processing

Simulation tickets for CMIP6 work can be raised on the CDDS Trac system (SRS login required) via 

- <a href="https://code.metoffice.gov.uk/trac/cdds/newticket?type=Simulation&milestone=Simulations%20v3.0&summary=Processing+for+CMIP6+simulation+%3Cmodel_id%3E+%3Cexperiment_id%3E+%3Cvariant_id%3E&description=See+ukcmip6:%3Cticket%3E.+`%3Cpackage%3E`+=``.%0D%0A`CDDS+version`:+`3.0.x`+(update+using+latest+version+from+source:/main/tags)+%0D%0ASuite/branch@revision:+``+%0D%0A%0D%0ASimulation+tickets+for+other+Packages:+%0D%0A[[TicketQuery(type=Simulation,summary~=%3Cmodel_id%3E+%3Cexperiment_id%3E+%3Cvariant_label%3E)]]%0D%0A%0D%0AThe+operational+procedure+for+using+CDDS+is+available+[wiki:CDDSOperationalProcedure+here]%0D%0A%0D%0AStreams+to+be+included+(delete+as+appropriate):%0D%0A+*+`ap4`+%0D%0A+*+`ap5`+%0D%0A+*+`apm`+%0D%0A+*+`apu`+%0D%0A+*+`ap6`+%0D%0A+*+`ap7`+%0D%0A+*+`ap8`+%0D%0A+*+`ap9`+%0D%0A+*+`onm`+%0D%0A+*+`inm`+%0D%0A+*+`ond`+%0D%0A%0D%0APlease+log+each+command+used+to+this+ticket."> Open a new operational simulation ticket (v3.0)</a>
- [CMIP6 Operational Procedure](operational_procedure/cmip6.md)
- [CMIP6 Simulation Ticket Review Procedure](operational_procedure/sim_review.md)
