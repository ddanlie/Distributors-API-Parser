import React, { createContext } from 'react';
import GlobalModals from "@/components/modals/global";
import Header from "@/components/header";

// export const DefaultLayoutContext = createContext();

const DefaultPageLayout = ({children}) => {
  return (
    <>
      {/* <DefaultLayoutContext.Provider value={{}}> */}
        <GlobalModals />
        <Header />
        {children}
      {/* </DefaultLayoutContext.Provider> */}
    </>
  );
}

export default DefaultPageLayout;
