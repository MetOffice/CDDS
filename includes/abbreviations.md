*[CDDS]: Climate Data Dissemination System
*[CMIP6]: Coupled Model Intercomparison Project
*[CMOR]: Climate Model Output Rewriter
*[Concatenation Tasks]: Concatenation Tasks are then run to join the files into a single file for a larger date range of length Concatenation Period. Concatenation Tasks are executed once per Concatenation Cycle.
*[Concatenation Period]: The length of the date range to be processed by 1 Concatenation Task.
*[CV]: Controlled Vocabulary. It is a pre-defined set of terms describing acceptable values for various quantities.
*[Controlled Vocabulary]: It is a pre-defined set of terms describing acceptable values for various quantities.
*[CREM]: Climate Research Experiment Management.
*[Data Request]: Information describing which MIP requested variables need to be produced for a given MIP-experiment combination. For CMIP6, see the CMIP6 Data Request.
*[Dataset]: A group of data containing some or all of the model output files from a single model simulation (i.e., model output files from a single realization of a single experiment from a single model).
*[Datasets]: Many groups of data containing some or all of the model output files from model simulations.
*[experiment]: A defined set of forcing inputs, and duration, for a model run.
*[Experiment]: A defined set of forcing inputs, and duration, for a model run.
*[Iris]: A Python library for Meteorology and Climatology.
*[MIP]: Model Intercomparison Project, e.g. ScenarioMIP.
*[MIP era]: The associated CMIP cycle, e.g. CMIP6
*[MIP output variable]: The final multi-dimensional data object that is written to an output netCDF file and corresponds to the MIP requested variable.
*[MIP requested variable]: The physical, generally observable concept for a given time sampling and level sampling (where applicable) that is fully identified by both the MIP requested variable name and the MIP table identifier.
*[MIP requested variables]: The physical, generally observable concept for a given time sampling and level sampling (where applicable). Every one is fully identified by both the MIP requested variable name and the MIP table identifier.
*[MIP requested variable name]: The short name of a physical, generally observable concept, e.g. tas.
*[MIP requested variable names]: The short names of physical, generally observable concepts, e.g. tas.
*[MIP table]: A text file that contains MIP-specific metadata constrained by the CF convention.
*[MIP tables]: Several MIP tables each ist a txt file that contains MIP-specific metadata constrained by the CP convention.
*[MIP table identifier]: A text code (e.g. Amon) identifying a MIP table.
*[MIP table identifiers]: Text codes (e.g. Amon) identifying corresponding MIP tables.
*[model configuration]: A recognised configuration of a climate model that is used for a wide variety of experiments / simulations.
*[model configurations]: Recognised configurations of climate models that are used for a wide variety of experiments / simulations.
*[model identifier]: A short name identifying a model, e.g. HadGEM3-GC31-LL.
*[model output files]: Output files produced from a modelling system, e.g. NEMO, CICE, that conform to a naming convention.
*[Model to MIP mapping configuration files]: A text file that can be read by the Python configparser containing one or more MIP requested variable names organised in sections; each section provides information about the model to MIP mapping.
*[model to MIP mapping configuration files]: A text file that can be read by the Python configparser containing one or more MIP requested variable names organised in sections; each section provides information about the model to MIP mapping.
*[model to MIP mapping]: Information providing details specifying which data are to be read from the model output files to create the input variables and how to process the input variables to produce a MIP output variable.
*[model type]: A text code (e.g. AOGCM, AGCM) identifying which model components are used in a given experiment / simulation.
*[output netCDF file]: A netCDF file produced by CMOR that is compliant with the MIP specifications and contains a single MIP output variable from a single model and a single simulation.
*[output netCDF files]: netCDF files produced by CMOR that are compliant with the MIP specifications and each contains a single MIP output variable from a single model and a single simulation.
*[netCDF]: Network Common Data Form
*[package]: An identifier indicating the phase of CDDS processing.
*[packages]: Identifiers indicating the phase of CDDS processing.
*[request file]: Information about a simulation used by all CDDS components.
*[request configuration]: Information about a simulation used by all CDDS components.
*[requested variables list]: A JSON file that describes which MIP requested variables can and will be produced for a given MIP-experiment combination from a specific version of the data request.
*[simulation]: A particular model run, with associated workflow identifier, which is defined by an experiment and has an assigned variant label.
*[simulations]: Particular model runs, with associated workflow identifiers, which are defined by an experiment and have an assigned variant label.
*[STASH]: Spatial and Temporal Averaging and Storage Handling.
*[stream identifier]: The name of a stream in the form (a|o)(d|p)(a-z), where (a|o) describes the aspect of the modelling system used to create the data in the stream i.e., a = atmosphere, o = ocean, (d|p) describes the status of the data i.e., d = dump and p = post processing, and a-z describes the grouping, e.g. m = monthly, s = seasonal, y = yearly.
*[stream identifiers]: The names of streams in the form (a|o)(d|p)(a-z), where each (a|o) describes the aspect of the modelling system used to create the data in the stream i.e., a = atmosphere, o = ocean, (d|p) describes the status of the data i.e., d = dump and p = post processing, and a-z describes the grouping, e.g. m = monthly, s = seasonal, y = yearly.
*[stream]: A group of data from a modelling system typically organised by time (e.g. daily, monthly, etc.).
*[streams]: Each stream is a group of data from a modelling system typically organised by time (e.g. daily, monthly, etc.).
*[suite identifier]: A text code (e.g. u-ar766) that identifies a model run.
*[user configuration file]: A file which is generated by CDDS Configure and used by MIP Convert.
*[User Configuration File]: A file which is generated by CDDS Configure and used by MIP Convert.
*[Variant label]: A code (e.g. r1i1p1f1) that uniquely identifies a simulation.
