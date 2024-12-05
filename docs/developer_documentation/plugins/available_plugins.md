# Available Plugins

## CIMP6 Plugin

| Responsible                        | Code Base                                                                                            |
|:-----------------------------------|:-----------------------------------------------------------------------------------------------------|
| [CDDS Team](mailto:cdds@metoffice.gov.uk) | [Link to code on GitHub](https://github.com/MetOffice/CDDS/tree/main/cdds/cdds/common/plugins/cmip6) |

The CMIP6 plugin provides all functionality needed for supporting CMIP6 projects. This is the default plugin for CDDS. When no plugin is given, 
the CMIP6 plugin will be loaded.

The plugin is implemented by the CDDS team. If you like any changes to this plugin, simply extend the plugin by a new one or speak with the 
CDDS team to make some improvements.

## CMIP6Plus Plugin

| Responsible                        | Code Base                                                                                                  |
|:-----------------------------------|:-----------------------------------------------------------------------------------------------------------|
| [CDDS Team](mailto:cdds@metoffice.gov.uk) | [Link to code on GitHub](https://github.com/MetOffice/CDDS/tree/main/cdds/cdds/common/plugins/cmip6_plus)  |

The CMIP6Plus plugin provides all functionality needed for supporting CMIP6Plus projects. This plugin is loaded if your MIP era in the request 
configuration file is `CMIP6Plus`.

The plugin is implemented by the CDDS team. If you like any changes to this plugin, simply extend the plugin by a new one or speak with the 
CDDS team to make some improvements.

## CORDEX Plugin

| Responsible                        | Code Base                                                                                              |
|:-----------------------------------|:-------------------------------------------------------------------------------------------------------|
| [CDDS Team](mailto:cdds@metoffice.gov.uk) | [Link to code on GitHub](https://github.com/MetOffice/CDDS/tree/main/cdds/cdds/common/plugins/cordex)  |

The CORDEX plugin provides all functionality needed for supporting CORDEX project. It is the only plugin that handles regional models and is 
supported by the CDDS team. This plugin is loaded if your MIP era in the request configuration file is `CORDEX`.

The plugin is implemented by the CDDS team. If you like any changes to this plugin, simply extend the plugin by a new one or speak with the 
CDDS team to make some improvements.

## GCModelDev Plugin

| Responsible                        | Code Base                                                                                                 |
|:-----------------------------------|:----------------------------------------------------------------------------------------------------------|
| [CDDS Team](mailto:cdds@metoffice.gov.uk) | [Link to code on GitHub](https://github.com/MetOffice/CDDS/tree/main/cdds/cdds/common/plugins/gcmodeldev) |

The GCModelDev plugin provides all functionality needed for supporting adhoc use of CDDS. This plugin is loaded if your MIP era in the 
request configuration file is `GCModelDev`.

The plugin is implemented by the CDDS team. If you like any changes to this plugin, simply extend the plugin by a new one or speak with the 
CDDS team to make some improvements.

## EERIE Plugin

| Responsible                       | Code Base                                                                                                               |
|:----------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| Jon Seddon                        | [Link to code on GitHub](https://github.com/MetOffice/CDDS/tree/CDDSO-318-eerie-plugin/cdds/cdds/common/plugins/eerie)  |

The EERIE plugin provides all functionality needed for supporting EERIE project. This plugin is loaded if your MIP era in the 
request configuration file is `EERIE`.

The plugin is implemented by Jon Seddon.

## SNAPSI Plugin

| Responsible                               | Code Base                                                                                       |
|:------------------------------------------|:------------------------------------------------------------------------------------------------|
| Matthew Mizielinski                       | [Link to code on GitHub](https://github.com/MetOffice/arise-cmor-tables/tree/master/cdds_arise) |

The SNAPSI plugin provides all functionality needed for supporting SNAPSI project. This plugin is loaded if your MIP era in the 
request configuration file is `SNAPSI` and the module path is given.

## ARISE Plugin

| Responsible                               | Code Base                                                                                       |
|:------------------------------------------|:------------------------------------------------------------------------------------------------|
| Matthew Mizielinski                       | [Link to code on GitHub](https://github.com/MetOffice/arise-cmor-tables/tree/master/cdds_arise) |

The ARISE plugin provides all functionality needed for supporting ARISE project. This plugin is loaded if your MIP era in the 
request configuration file is `ARSIE` and the module path is given.

The plugin is implemented by Matthew Mizielinski.
