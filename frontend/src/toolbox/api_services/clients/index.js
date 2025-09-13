import { 
    postData, 
    getData, 
    patchData, 
    putData, 
    deleteData,
    uploadFile
} from "@/toolbox/utils/api/axiosApiUtils";


export const service_clients_read_async_distributors_names = async (params) => {
    try {
        const response_data = await getData("/clients/distributors_names", { params });
        return response_data;
    } catch (error) {
        console.error("Error fetching distributors names:", error);
        throw error;
    }
};
