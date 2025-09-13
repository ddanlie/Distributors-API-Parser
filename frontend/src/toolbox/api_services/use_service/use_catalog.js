import { useMutation, useQuery } from "@tanstack/react-query";

import { 
    catalog_read_async_filtered_catalog,
    catalog_read_async_items_properties,
    catalog_read_async_items_filters
} from '../queryKeys'

import {
    service_catalog_read_async_items_properties,
    service_catalog_read_async_items_filters,
    service_catalog_read_async_filtered_catalog
} from "../catalog"

export const use_service_catalog_read_async_filtered_catalog = ({body, config={}}) => {
    return useQuery({
        queryKey: [
            catalog_read_async_filtered_catalog,
        ],
        queryFn: () => service_catalog_read_async_filtered_catalog(body),
        ...config
    });
};

export const use_service_catalog_read_async_items_properties = ({body, config={}}) => {
    return useQuery({
        queryKey: [
            catalog_read_async_items_properties, 
        ],
        queryFn: () => service_catalog_read_async_items_properties(body),
        ...config
    });
};

export const use_service_catalog_read_async_items_filters = ({body, config={}}) => {
    return useQuery({
        queryKey: [
            catalog_read_async_items_filters, 
        ],
        queryFn: () => service_catalog_read_async_items_filters(body),
        ...config
    });
};