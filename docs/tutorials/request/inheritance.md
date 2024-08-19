# Inheritance Section

The `inheritance` in the request configuration is optional and contains a path to a template for the request.

## Configuration Values

`template`
:   path to the template for the request that contains values that will be added to the request configuration. 
    The request configuration can override values in the template.

## Examples

!!! example
    ```yaml
    [inheritance]
    template = /path/to/request-template.cfg
    ```