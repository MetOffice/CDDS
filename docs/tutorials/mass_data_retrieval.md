# Mass data retrieval

If desired, data can be retrieved from MASS using our cdds_retrieve_data tool. This
can be used locally, via SPICE or JASMIN.

It's benefits include:

- Copying the directory structure associated with the files.
- Customisable chunking to reduce load on infrastructure during retrieval.
- A dry run option to print actions without retrieving the files.


## Using it from the command line

      ```
      cdds_retrieve_data <moose_base_path> <base_dataset_id> <variable_file> <>
      ```

## Preconditions

- [x] Check that you, add the CDDS project (at least the `cdds_common` package) is in your Python path.

???example
    To make sure that the CDDS project is in your Python path by using a script
    ```bash
    load_conda() {
        # load conda environment
        . ~cdds/software/miniconda3/bin/activate <cdds_conda_version>
    }

    setup_cdds_package() {
        # add cdds_common containing plugins implementation to PATH
        # Setup CDDS project
        local cdds_dir=<path-to-cdds-project>
        local cdds_package="cdds"

        # Update PATH:
        if [ -d $cdds_dir/$cdds_package/bin ]; then
            export PATH=$cdds_dir/$cdds_package/bin:$PATH
        fi

        # Update PYTHONPATH:
        if [ -d $cdds_dir/$cdds_package]; then
            export PYTHONPATH=$cdds_dir/$cdds_package:$PYTHONPATH
        fi
    }

    setup_project() {
        <setup-your-project>
    }

    load_conda
    setup_cdds_package
    setup_project
    ```

    - [x] Set `<cdds_conda_version>` to the conda version of the CDDS project you want to use (e.g. `cdds-3.0_dev-0`)
    - [x] Set the `<path-to-cdds-project>` to the path to the CDDS project.
    - [x] Replace `<setup-your-project>` with the commands you need to setup your project.

## Step 1: Create a plugin class

- [x] Create a module `<my>_plugin.py` where `<my>` can be replaced with any name you like. A good choice would be the MIP era that the plugin should support.
- [x] Import `CddsPlugin` from CDDS project:
      ```python
      from cdds.common.plugins.plugins import CddsPlugin
      ```
- [x] Create a plugin class that extends from the `CddsPlugin` class:
      ```python
      class MyPlugin(CddsPlugin):
      ```

!!!info
    If you use Pycharm, you have the benefit that you can move your cursor to the class name (here: `MyPlugin`) and press `ALT + Enter`. You should now see 
    an option to `Implement abstract methods`, select it. The methods you have to implement will be automatically add to your class. The same is with the 
    imports that are needed.

- [x] Add the `__init__` method. This method must call the `__init__` method of the super class with the parameter mip_era. The mip_era is the one that your 
      plugin should support.
- [x] To implement all methods you need a `ModelParameters` class, a `GridLabel` and a `StreamInfo` class. How to create this classes, will be explained in 
      next sections.

???example
    ```python
    from typing import Type

    from cdds_common.cdds_plugins.grid import GridLabel
    from cdds_common.cdds_plugins.models import ModelParameters
    from cdds_common.cdds_plugins.plugins import CddsPlugin
    from cdds_common.cdds_plugins.streams import StreamInfo


    class MyPlugin(CddsPlugin):
    
        def __init__(self):
            super(MyPlugin, self).__init__('my_mip_era')
    
        def models_parameters(self, model_id: str) -> ModelParameters:
            pass

        def overload_models_parameters(self, source_dir: str) -> None:
            pass

        def grid_labels(self) -> Type[GridLabel]:
            pass

        def stream_info(self) -> StreamInfo:
            pass
    
    ```

For the moment, we leave the plugin class like it is and take a look at the `ModelParameters` class and `GridLabel` class 
and `StreamInfo` class. We will come back to the plugin class later again.

## Step 2: Create the model parameters class

You should create one model parameter class for each model you want to support. For demonstration, here we only show you 
to create one model parameter class. To create more classes, simple repeat the steps.

!!!note
    You can use the same module or another one. In my demonstration project, I used another module to implement everything 
    that is related to the model parameters.

- [x] Import the `ModelParameters` class from the CDDS project:
      ```python
      from cdds.common.plugins.models import ModelParameters
      ```
- [x] Create a class that extends from the `ModelParameters`
- [x] Add the abstract methods that must be implemented (Pycharm can help you with that see in the First Step)
- [x] Add default `__init__` method.

???example
    ```python
    from typing import List, Dict

    from cdds_common.cdds_plugins.grid import GridType, GridInfo
    from cdds_common.cdds_plugins.models import ModelParameters


    class MyModelParams(ModelParameters):
        def __init__(self):
            super(MyModelParams, self).__init__()

        @property
        def model_version(self) -> str:
            pass

        @property
        def data_request_version(self) -> str:
            pass

        @property
        def um_version(self) -> str:
            pass
    
        def grid_info(self, grid_type: GridType) -> GridInfo:
            pass
    
        def temp_space(self, stream_id: str) -> int:
            pass
        
        def memory(self, stream_id: str) -> str:
            pass
        
        def cycle_length(self, stream_id: str) -> str:
            pass
    
        def sizing_info(self, frequency: str, shape: str) -> float:
            pass
    
        def full_sizing_info(self) -> Dict[str, Dict[str, float]]:
            pass
    
        def is_model(self, model_id: str) -> bool:
            pass
    
        def subdaily_streams(self) -> List[str]:
            pass
    ```

- [x] Implement all method except the `grid_info` method.

Next step is to implement the `GridInfo` classes.

## Step 3: Implement grid information classes

!!!note
    You can use the same module or another one. In my demonstration project, I used another module to implement everything 
    that is related to the grid information.

- [x] Import the `GridInfo` class and `GridType` enum from the CDDS project:
      ```python
      from cdds.common.plugins.grid import GridType, GridInfo
      ```
- [x] For each grid type, there should be an own grid information class. So, create two classes that extends from the 
      `GridInfo` - one for the atmosphere grid and one for the ocean grid.
- [x] Add the abstract methods that must be implemented (Pycharm can help you with that see in the First Step)
- [x] Add the `__init__` methods that call the super `__init__` method and has a parameter the supported grid type of your grid information class.
- [x] Implement the methods.

!!!note
    Often the masks method is not implemented (simple: return `None`) for atmosphere grids.

???example "Example class for atmosphere grid"
    ```python
    from typing import List, Dict

    from cdds.common.plugins.grid import GridType, GridInfo, OceanGridPolarMask

    class MyAtmosGridInfo(GridInfo):
        def __init__(self):
            super(MyAtmosGridInfo, self).__init__(GridType.ATMOS)
        
        @property
        def model_info(self) -> str:
            pass
    
        @property
        def nominal_resolution(self) -> str:
            pass
    
        @property
        def longitude(self) -> int:
            pass
    
        @property
        def latitude(self) -> int:
            pass

        @property
        def v_latitude(self) -> int:
            pass

        @property
        def levels(self) -> int:
            pass
    
        @property
        def masks(self) -> Dict[str, OceanGridPolarMask]:
            pass

        @property
        def replacement_coordinates_file(self) -> str:
            pass
    
        def ancil_filenames(self) -> List[str]:
            pass

        def hybrid_heights_files(self) -> List[str]:
            pass
    ```

???example "Example class for ocean grid"
    ```python
    from typing import List, Dict

    from cdds.common.plugins.grid import GridType, GridInfo, OceanGridPolarMask


    class MyOceanGridInfo(GridInfo):
    
        def __init__(self):
            super(MyOceanGridInfo, self).__init__(GridType.OCEAN)
    
        @property
        def model_info(self) -> str:
            pass

        @property
        def nominal_resolution(self) -> str:
            pass

        @property
        def longitude(self) -> int:
            pass

        @property
        def latitude(self) -> int:
            pass

        @property
        def v_latitude(self) -> int:
            pass

        @property
        def levels(self) -> int:
            pass

        @property
        def masks(self) -> Dict[str, OceanGridPolarMask]:
            pass

        @property
        def replacement_coordinates_file(self) -> str:
            pass

        def ancil_filenames(self) -> List[str]:
            pass

        def hybrid_heights_files(self) -> List[str]:git 
            pass
    ```

The next step is to use your grid information classes in your model parameters class.

## Step 4: Use your grid information classes in your model parameters class

- [x] Implement the `grid_info` method in your model parameters class such that it returns the right grid information class according the grid type.

???example
    ```python
    def grid_info(self, grid_type: GridType) -> GridInfo:
        if grid_type == GridType.ATMOS:
             return MyAtmosGridInfo()
        elif grid_type == GridType.OCEAN:
             return MyOceanGridInfo()
        else:
             raise ValueError("Unsupported grid type: {}".format(GridType))
    ```

### Step 5: Use your model parameters class in your plugin

- [x] Go to your plugin class and implement the `model_parameters` method. This method should return the corresponding model parameters class according 
      the model ID.

???example
    ```python
    def models_parameters(self, model_id: str) -> ModelParameters:
        model_params = {
            'MyModel': MyModelParams()
        }
        return model_params[model_id]
    ```

- [x] If you allow overloading the defined parameters in your `ModelParameters` classes, then implement the `overload_models_parameters` method.

The last to do for finishing the plugin is to implement the `GridLabel`


### Step 6: Implement the grid labels

- [x] Import the `GridLabel` class from CDDS:
      ```python
      from cdds.common.plugins.grid import GridLabel
      ```
- [x] Create a class your own grid label enum class that extend from GridLabel with a `__init__` method that as the arguments `grid_name`, 
      `label` and `extra_info`

???example
    ```python
    class MyGridLabel(GridLabel):
    
        def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
            self.grid_name = grid_name
            self.label = label
            self.extra_info = extra_info
    
        @classmethod
        def from_name(cls, name: str) -> 'GridLabel':
            pass
    ```

- [x] Add the grid label you want to support.

???example
    Here, `MyGridLabel` should support `NATIVE` or `NATIVE_ZONAL`.
    ```python
    class MyGridLabel(GridLabel):
    
        def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
            self.grid_name = grid_name
            self.label = label
            self.extra_info = extra_info
    
        @classmethod
        def from_name(cls, name: str) -> 'GridLabel':
            for grid_label in MyGridLabel:
                if grid_label.grid_name == name.lower():
                    return grid_label
            raise KeyError('Not supported grid labels for {}'.format(name))

        NATIVE = 'native', 'gn', False
        NATIVE_ZONAL = 'native-zonal', 'gnz', False
    ```

## Step 7: Use your grid labels in your plugin

- [x] Implement the `grid_labels` in your plugin by simply returning your grid label enum class

???example
    ```python
    def grid_labels(self) -> Type[GridLabel]:
        return MyGridLabel
    ```

## Step 8: Implement the stream info class

You should create a stream info class for all information around streams.

- [x] Import the `StreamInfo` class from the CDDS project:
      ```python
      from cdds.common.plugins.streams import StreamInfo
      ```
- [x] Create a class that extends from the `StreamInfo`
- [x] Add the abstract methods that must be implemented (Pycharm can help you with that see in the First Step)
- [x] Add `__init__` method
- [x] Implement all necesary methods

???example
    ```python
    class MyStreamInfo(StreamInfo):
        def __init__(self, config_path: str = '') -> None:
            super(Cmip6StreamInfo, self).__init__(config_path)

        def _load_streams(self, configuration: Dict[str, Any]) -> None:
            pass

        def retrieve_stream_id(self, variable: str, mip_table: str) -> Tuple[str, str]:
            pass
    ```

### Step 9: Use your stream info in your plugin

- [x] Use the `stream_info` in your plugin by simply returning your stream info

???example
    ```python
    def stream_info(self) -> StreamInfo:
        return MyStreamInfo()
    ```

Congratulations, you finished to implement the plugin. Now, you can use it with CDDS.

### Step 10: Use your plugin with CDDS

- [x] Add your implementation to the `PYTHONPATH` (and `PATH`). Otherwise, CDDS will not be able to find it.
- [x] Change the value of the `external_plugin_location` in the `request.cfg` file to the path to your plugin implementation
- [x] Change the value of the `external_plugin` in the `request.cfg` file to the module path to your plugin

???example "Example: Change values for the ARISE plugin"
    ```
    external_plugin_location = /project/cdds/arise
    external_plugin = arise.plugin
    ```
