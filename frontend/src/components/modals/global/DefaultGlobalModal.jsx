import React from 'react';
import { DefaultModal } from "@/components/modals/DefaultModal";

// This could be some dynamic modal that reacts to some events
// Or an invisible/dynamic tracker for some states/api calls
const DefaultGlobalModal = ({children}) => {
  return (
    <DefaultModal
      open={true} // always opened, global modals are added and deleted dynamically
      coverable={true} // global modals can be always by other modals
    >
      {children}
    </DefaultModal>
  );
}

export default DefaultGlobalModal;