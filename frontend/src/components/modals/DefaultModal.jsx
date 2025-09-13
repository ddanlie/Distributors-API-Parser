import React, { useEffect, useState } from "react";
import { atom, useAtom } from "jotai";

// This state gives an ability
// to recursively open modals above each other
// until uncoverable modal comes on top
// YOU can use this state for custom reactions to it
const allModalsStateAtom = atom({
    // Do not change this inital state
    some_modal_is_opened: false,
    is_opened_modal_coverable: false
})

// This component is used to detect "open" state changes
// and change/react to allModalsState
const DefaultModalHelper = ({
    children,
    coverable=false,
    allModalsState,
    setAllModalsState
}) => {

    // React to state
    // Let's check all combinations together
    // - comb. case  1 2 3 4
    // - some_opened T T F F
    // - coverable   T F T F
    // case 1 - something is opened? don't care - its coverable, go render
    // case 2 - something is opened? it's not coverable so get out of here
    // case 3 - invalid state, must not happen
    // case 4 - initial state - nothing opened? coverable is false - ok, go render
    if (
        allModalsState.some_modal_is_opened
        && 
        !allModalsState.is_opened_modal_coverable
    ) {
        return null;
    }

    // Change state on mount/unmount
    const [ 
        previousState,
        setPreviousState
    ] = useState(false);
    useEffect(() => {
        // Remember previous
        setPreviousState(allModalsState);
        // mount
        setAllModalsState({
            some_modal_is_opened: true,
            is_opened_modal_coverable: coverable
        })
        // unmount
        return () => {
            let no_modals_left = previousState.some_modal_is_opened === false;
            if (no_modals_left) {
                setAllModalsState({
                    some_modal_is_opened: false,
                    is_opened_modal_coverable: false
                });
            }
            else {
                setAllModalsState({
                    some_modal_is_opened: true,
                    is_opened_modal_coverable: previousState.is_opened_modal_coverable
                });
            }
        };
    },[]);

    return (
        <div>
            {children}
        </div>
    )
}

// This component is a pure logic block tracking which modals are open
// and won't let another one to be opened if it is not set explicitly by "coverable"
const DefaultModal = ({
    children,
    open=false, //set some "opened" state to this variable
    coverable=false //if modal can be covered by other modals 
}) => {

  const [allModalsState, setAllModalsState] = useAtom(allModalsStateAtom);

  if (!open)
    return null;

  return (
    <DefaultModalHelper
      allModalsState={allModalsState}
      setAllModalsState={setAllModalsState}
      coverable={coverable}
    >
      {children}
    </DefaultModalHelper>
  );
}


// Defaut modal with some styles. Create your own here or somewhere else
const DefaultModalElement = ({
    children,
    open=false,
    coverable=false
}) => {

    return (
        <DefaultModal
            open={open}
            coverable={coverable}
        >
            <div className={`
                fixed inset-0 z-50 flex 
                items-center justify-center 
                bg-black bg-opacity-50
                p-6
                bg-white
            `}>
                {children}
            </div>
        </DefaultModal>
    )
}

export { 
    allModalsStateAtom, 
    DefaultModal,
    DefaultModalElement
};
