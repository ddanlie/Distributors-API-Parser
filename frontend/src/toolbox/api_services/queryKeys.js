// CREATE
// create_*
// READ
    // read_async_* - asynchronious requests
    // read_sync_* - synchronious requests (use in very specific cases (idk in which ones))
// UPDATE
    // update_*  
// DELETE
    // delete_*

// Each operation prefix is a service: clients_*, catalog_* etc...
// Clients Service
export const clients_read_async_distributors_names      = "CLIENTS_READ_ASYNC_DISTRIBUTORS_NAMES"

// Catalog Service
export const catalog_read_async_filtered_catalog        = "CATALOG_READ_ASYNC_FILTERED_CATALOG"
export const catalog_read_async_items_properties        = "CATALOG_READ_ASYNC_ITEMS_PROPERTIES"
export const catalog_read_async_items_filters           = "CATALOG_READ_ASYNC_ITEMS_FILTERS"