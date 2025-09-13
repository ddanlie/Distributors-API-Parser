import axiosInstance from "./axiosInstance";

// GET request
export const getData = async (url, config = {}) => {
  const { params, ...axiosConfig } = config;
  const response = await axiosInstance.get(url, {
    params,
    ...axiosConfig,
  });
  return response.data;
};

// POST request
export const postData = async (url, body, config) => {
  const { data } = await axiosInstance.post(url, body, config);
  return data;
};

// PUT request
export const putData = async (url, body) => {
  const { data } = await axiosInstance.put(url, body);
  return data;
};

// PATCH request
export const patchData = async (url, body) => {
  const { data } = await axiosInstance.patch(url, body);
  return data;
};

// DELETE request
export const deleteData = async (url) => {
  const { data } = await axiosInstance.delete(url);
  return data;
};

// UPLOAD file(s) with multipart/form-data
export const uploadFile = async (
  url,
  files,
  additionalData = {},
  onProgress = null
) => {
  const formData = new FormData();
  // Append file(s)
  if (Array.isArray(files)) {
    files.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });
  } else {
    formData.append("file", files);
  }

  // Append additional data
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value);
  });

  const config = {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  };

  if (onProgress) {
    config.onUploadProgress = (event) => {
      const progress = (event.loaded * 100) / event.total;
      onProgress(progress / 100); // ✅ Return more 0-1 range
    };
  }

  const { data } = await postData(url, formData, config);
  return data;
};
