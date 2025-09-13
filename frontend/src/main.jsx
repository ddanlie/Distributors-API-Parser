import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import logo from '@/assets/logo.svg'; - use @ for src/ instead of ../../../../../

import App from "./App";
import DevComponent from "./dev_component";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {/* <DevComponent /> */}
    </QueryClientProvider>
  </React.StrictMode>
);