import { 
    postData, 
    getData, 
    patchData, 
    putData, 
    deleteData,
    uploadFile
} from "@/toolbox/utils/api/axiosApiUtils";


export const service_catalog_read_async_filtered_catalog = async (body) => {
    try {
        const response_data = await postData("/catalog/filtered_catalog", body );
        return response_data;
    } catch (error) {
        console.error("Error fetching filtered catalog:", error);
        throw error;
    }
};

export const service_catalog_read_async_items_properties = async (body) => {
    try {
        const response_data = await postData("/catalog/items_properties", body );
        return response_data;
    } catch (error) {
        console.error("Error fetching items properties:", error);
        throw error;
    }
};

export const service_catalog_read_async_items_filters = async (body) => {
    try {
        const response_data = await postData("/catalog/items_filters", body);
        return response_data;
    } catch (error) {
        console.error("Error fetching items filters:", error);
        throw error;
    }
};
