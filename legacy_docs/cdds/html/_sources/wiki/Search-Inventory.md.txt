# Script: `search_inventory`

In release v1.6.0 we've added an inventory (updated each night) that is used by CDDS Prepare to avoid the need for combined "approved_variables" files to avoid duplicating previously provided data.

The script allows the user to search the inventory using data set id patterns which can include wildcards **instead** of a particular "facet".

## The inventory database

We generate a small sqlite3 database each night from the contents of MASS. As such this only contains data that we have produced within the Met Office and archived to MASS.

## Data set ids and "facet" structure

The dataset ids used in CMIP6 are made up of a set of "facets", strings describing some aspect of what the data relates to. A facet may be the name of the MIP, experiment_id or variable name.

The format for CMIP6 is

    CMIP6.<activity id (MIP)>.<institution id>.<source_id (model)>.<experiment id>.<variant label>.<MIP table>.<variable id>.<grid label>

e.g.
    `CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.historical.r1i1p1f2.Amon.tas.gn`

## Search for datasets matching a facet pattern.

The data set id used for the inventory is a set of 9 facets joined by dots. To search for all UKESM1 daily precipitation datasets you can run

```bash
search_inventory CMIP6.*.*.UKESM1-0-LL.*.*.day.pr.*
```
Which at the time of writing returns
```

Mip Era Mip    Institute  Model              Experiment      Variant    Mip Table  Variable Name        Grid Status     Version    Facet String
CMIP6   AerChemMIP MOHC       UKESM1-0-LL        hist-piAer      r1i1p1f2   day        pr                   gn   available  v20190813  CMIP6.AerChemMIP.MOHC.UKESM1-0-LL.hist-piAer.r1i1p1f2.day.pr.gn
CMIP6   AerChemMIP MOHC       UKESM1-0-LL        hist-piAer      r2i1p1f2   day        pr                   gn   available  v20191104  CMIP6.AerChemMIP.MOHC.UKESM1-0-LL.hist-piAer.r2i1p1f2.day.pr.gn
...
CMIP6   ScenarioMIP MOHC       UKESM1-0-LL        ssp585          r4i1p1f2   day        pr                   gn   available  v20190814  CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp585.r4i1p1f2.day.pr.gn
CMIP6   ScenarioMIP MOHC       UKESM1-0-LL        ssp585          r8i1p1f2   day        pr                   gn   available  v20190906  CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp585.r8i1p1f2.day.pr.gn

A total of 239 records were found.
```

## Locating data in MASS

If you require the list of files in MASS for a particular dataset then the `-s` option will provide this for each data set matching the pattern in the inventory. For example

```bash
search_inventory CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp585.r3i1p1f2.*.pr.gn -s
```
returns
```

Mip Era Mip    Institute  Model              Experiment      Variant    Mip Table  Variable Name        Grid Status     Version    Facet String
CMIP6   ScenarioMIP MOHC       UKESM1-0-LL        ssp585          r3i1p1f2   Amon       pr                   gn   available  v20190507  CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp585.r3i1p1f2.Amon.pr.gn
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/Amon/pr/gn/available/v20190507
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/Amon/pr/gn/available/v20190507/pr_Amon_UKESM1-0-LL_ssp585_r3i1p1f2_gn_201501-204912.nc
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/Amon/pr/gn/available/v20190507/pr_Amon_UKESM1-0-LL_ssp585_r3i1p1f2_gn_205001-210012.nc

CMIP6   ScenarioMIP MOHC       UKESM1-0-LL        ssp585          r3i1p1f2   day        pr                   gn   available  v20190813  CMIP6.ScenarioMIP.MOHC.UKESM1-0-LL.ssp585.r3i1p1f2.day.pr.gn
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/day/pr/gn/available/v20190813
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/day/pr/gn/available/v20190813/pr_day_UKESM1-0-LL_ssp585_r3i1p1f2_gn_20150101-20491230.nc
moose:/adhoc/projects/cdds/production/CMIP6/ScenarioMIP/MOHC/UKESM1-0-LL/ssp585/r3i1p1f2/day/pr/gn/available/v20190813/pr_day_UKESM1-0-LL_ssp585_r3i1p1f2_gn_20500101-21001230.nc


A total of 2 records were found.
```

Note that in this case a `moo ls` command is run for each data set found.