import sys, re
from cdds.common.mappings.mapping import ModelToMip
from cdds.common.plugins.plugin_loader import load_plugin

infile = sys.argv[1]

var_list = []
with open(infile, "r") as fh:
    for line in fh.readlines():
        table, variable, stream = re.match('(\S+)/([a-zA-Z0-9-]+):?(\S+)?', line).groups()
        var_list.append({'table': table, 'name': variable, 'stream': stream})


request = {"science": {"mip_era": "GCModelDev", "model_id": "HadREM-CP4A-4p5km",
                       "model_ver": "1.0"},
           }

load_plugin('GCModelDev')


for entry in var_list:
    request['variables'] = [entry]

    try:
        mass_filters = ModelToMip(request).mass_filters()

        for stream, results in mass_filters.items():
            print("\n")
            print("Stream {}: (Default)".format(stream))
            for result in results:
                print("\t{table}/{name}:".format(**result))

                for constraint in result['constraint']:
                    print("\t\t{}".format(constraint))


    except Exception as err:
        print(err)
