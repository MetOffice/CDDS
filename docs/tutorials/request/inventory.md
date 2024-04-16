# Inventory Section

The `inventory` section in the request configuration contains all settings to connect to and manage the inventory database.

## Configuration Values

`inventory_check`
:   specify if the inventory should be used to determine of a variables is active or not.

    **Default:** `False`

`inventory_database_location`
:   the path to the inventory database.

## Examples

!!! example
    ```yaml
    [inventory]
    inventory_check = True
    inventory_database_location = /home/user/inventory.db
    ```
