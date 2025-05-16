# Mapping Plugin Framework

## Overview

The mapping plugin framework was designed using an object-oriented approach. This framework allows you to customise and 
extend MipConvert. Mapping plugins are loaded at runtime from a specific given path. A mapping plugin is a bundle that 
adds functionality to MIP Convert such that the appropriate mapping can be set and used for different models 
(e.g. UKESM1 or HadGEM3). This also allows third party developers to add mapping functionality to MipConvert without 
having access to the source code. 

The mapping plugin framework loads the specific plugin into a plugin store that stores it during runtime. This avoids
excessive loading of the plugin. The MIP Convert code gets access to the plugin via the plugin store.

![Plugin Overview](images/mapping-plugin-overview.png){ width="900" }

## Mapping Plugin Structure
A mapping plugin is a construct that allows the user/developer to define the method for calculating particular 
variables by MIP Convert. 

A mapping plugin contains both the mappings that define variables and additional "processor" functions used 
to calculate more complex variables.

The design of a plugin is illustrated in the below diagram:
![Plugin Overview](images/mapping-plugin-structure.png){ width="900" }

The red boxes represent classes, the blue one a singleton class and the yellow ones modules. The green one represent all 
mapping configuration files.

A mapping plugin is loaded by the mapping plugin loader and registered to the mapping plugin store. The mapping plugin 
is stored and cached during runtime. Each mapping plugin contains information about the supported model family. 

The processors module containing all processing function that are needed to CMORise the models with the given mapping
configurations. The processing functions are different for each model family.

The constants module provides all the constants that can be used in the mapping configuration files.

The quality control modules contains the functionality how to check the data against min and max bounds. This is rarely 
used in practise.
