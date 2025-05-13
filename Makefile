## Creates the directory structure for adding a new mapping plugin
## Usage: make new-mapping-plugin-tree model=your_model_name
model ?= model
lower_model = $(shell echo $(model) | tr A-Z- a-z_)

new-mapping-plugin-tree:
	mkdir -p mip_convert/mip_convert/plugins/$(lower_model)
	mkdir -p mip_convert/mip_convert/plugins/$(lower_model)/data
	touch mip_convert/mip_convert/plugins/$(lower_model)/__init__.py
	touch mip_convert/mip_convert/plugins/$(lower_model)/$(lower_model)_plugin.py
	touch mip_convert/mip_convert/plugins/$(lower_model)/data/__init__.py
	touch mip_convert/mip_convert/plugins/$(lower_model)/data/processors.py
