import axios from "axios";
import { AXIOS_BASE_API_URL } from "@/env/env.active.js"


const axiosInstance = axios.create({
  baseURL: AXIOS_BASE_API_URL,
  timeout: 100000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
  },
});

export default axiosInstance;
