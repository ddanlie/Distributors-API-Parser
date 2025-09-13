import { useMutation, useQuery } from "@tanstack/react-query";

import {
    clients_read_async_distributors_names
} from '../queryKeys'

import {
    service_clients_read_async_distributors_names 
} from "../clients"


export const use_service_clients_read_async_distributors_names = ({params, config={}}) => {
    return useQuery({
        queryKey: [clients_read_async_distributors_names, params],
        queryFn: () => service_clients_read_async_distributors_names(params),
        ...config
    });
};
