// These filters are not cheking any mistakes in types
// You should create separate e.g. Formik components to 
// validate the output of filters callbacks

import React, { useEffect, useState } from "react";
import assets, {ResizableAsset} from "@/toolbox/utils/assets/importAllAssets.jsx";
import { RadioChoice } from "@/components/choice";
import Selector from "@/components/selector";
import { atom, useAtom } from "jotai";
import { atomFamily }  from "jotai/utils";

export const resetFilterAtomFamily = atomFamily(
  () => atom(false) // default false
);
// Usage example:
//
// - For unstable groups:
// **declare out of your component**
// function ClientFilterReset({ clientName, onInit }) {
//   const resetSignal = useSetAtom(resetFilterAtomFamily(`${clientName}_filters_group`));

//   useEffect(() => {
//     onInit(clientName, {
//       resetSignal,
//       resetGroupId: `filter_group_${clientName}`,
//     });
//   }, [clientName, resetSignal, onInit]);

//   return null; // nothing rendered
// }
//**in parent**
// const [clientFiltersGroupMap, setClientFiltersGroupMap] = useState({});

// const distributors_names = ["x", "y"]//the trick is - this is not stable (e.g. fetched from query )
// distributors_names?.map(name => (
// <ClientFilterReset
//     key={name}
//     clientName={name}
//     onInit={(k, v) =>
//     setClientFiltersGroupMap(prev => ({ ...prev, [k]: v }))
//     }
// />
// ));
// <FilterResetter resetFilterIds={["a", "x_distributor_filter_group"]} />
// <FilterResetter resetFilterIds={["a", "y_distributor_filter_group"]} />
// <button onClick={clientFiltersGroupMap["x"].resetSignal(true)}>Reset "x" group</button>
// <button onClick={clientFiltersGroupMap["y"].resetSignal(true)}>Reset "y" group</button>
//
// - For stable lengths:
// just use the .map approach 
//
// - For one group:  
// const setResetSignalForDefault = useSetAtom(resetFilterAtomFamily("all filters"));
// setResetSignalForDefault(true)
// <NumberFilter resetFilterIds=["all filters group", "filters group 1"]/>

const FilterResetter = ({
    handleReset=()=>{},
    resetFilterId="<Default Id>",
}) => {
    const [resetSignal, setResetSignal] = useAtom(resetFilterAtomFamily(resetFilterId));

    useEffect(() => {
        if (resetSignal) {
            handleReset();
            setResetSignal(false); // clear after use
        }
    }, [resetSignal]);

    return <></>;
};


const FilterHeader = ({
    propertyName="<Property Name>",
    unit=null,
    handleReset=()=>{},
    widthPx=-1,//if < 0 - 100%
    resetFilterIds=[]// each id is a group to which filter belongs to for resetting
}) => {

    return (
        <>
        <div className="flex justify-between w-full" style={{ maxWidth: `${widthPx}px` }}>
            <h1 className="
                flex items-start text-left
                text-itbs-annotation-small
                break-words
                line-clamp-3
            ">
                {`${propertyName}`+`${unit ? ` [${unit}] ` : ''}`}
            </h1>
            <div className="hover:cursor-pointer" onClick={()=>{handleReset()}}>
                <ResizableAsset className="flex flex-1" asset_from_assets={assets.interactives.Restart} w={15} h={15} />
            </div>
        </div>
        {resetFilterIds.map((resetFilterId, index) => (
            <FilterResetter key={index} resetFilterId={resetFilterId} handleReset={handleReset} />
        ))}
        </>
    )
}

const NumberFilter = ({
    onResetFilter=(maxValue, minValue, name, id) => {},
    onValueChange=(maxValue, minValue, name, id) => {},
    ref=null,
    propertyName="<Property Name>",
    propertyId="<Property ID>",
    unit="pcs",
    defaultMinValue=0,
    defaultMaxValue=100,
    widthPx=-1,//if < 0 - 100%
    resetFilterIds=[]
}) => {
    const [minValueState, setMinValueState] = useState(defaultMinValue);
    const [maxValueState, setMaxValueState] = useState(defaultMaxValue);
    const [redIndicatorMaxState, setRedIndicatorMaxState] = useState(false);
    const [redIndicatorMinState, setRedIndicatorMinState] = useState(false);


    const doWarningMax = () => {
        setRedIndicatorMaxState(true);
        setTimeout(() => {
            setRedIndicatorMaxState(false);
        }, 300);
    };

    const doWarningMin = () => {
        setRedIndicatorMinState(true);
        setTimeout(() => {
            setRedIndicatorMinState(false);
        }, 300);
    };

    const handleMaxChange = (event) => {
        if(!event.currentTarget.value) {
            // setMaxValueState(defaultMaxValue); - just don't send any signals
            return;
        }
        const newMaxValue = Number(event.currentTarget.value);
        console.log(`Max value is now: ${maxValueState}`);
        console.log(`Max value to set: ${maxValueState}`);
        if (newMaxValue >= minValueState) {
            if(newMaxValue === defaultMaxValue && minValueState == defaultMinValue) {
                handleReset();
                return;
            }
            setMaxValueState(newMaxValue);
            onValueChange({
                maxValue:newMaxValue,
                minValue:minValueState,
                name:propertyName,
                id:propertyId
            });
        }
        else {
            console.log(`Setting max value to ${minValueState}`);
            setMaxValueState(minValueState);
            onValueChange({
                maxValue:minValueState,
                minValue:minValueState,
                name:propertyName,
                id:propertyId
            });
            doWarningMin();//on purpose
        }
        
    };

    const handleMinChange = (event) => {
        if(!event.currentTarget.value) {
            // setMinValueState(defaultMinValue); - its dirty, i coudln't even erase a 0 from my input
            // just don't send any signals 
            return;
        }
        const newMinValue = Number(event.currentTarget.value);
        console.log(`Min value is now: ${minValueState}`);
        console.log(`Min value to set: ${newMinValue}`);
        if (newMinValue <= maxValueState) {
            if(newMinValue === defaultMinValue && maxValueState == defaultMaxValue) {
                handleReset();
                return;
            }
            setMinValueState(newMinValue);
            onValueChange({
                minValue:newMinValue,
                maxValue:maxValueState,
                name:propertyName,
                id:propertyId
            });
        }  
        else {
            setMinValueState(maxValueState);
            onValueChange({
                minValue:maxValueState,
                maxValue:maxValueState,
                name:propertyName,
                id:propertyId
            });
            doWarningMax();//on purpose
        }
       
    };

    const handleReset = () => {
        setMinValueState(defaultMinValue);
        setMaxValueState(defaultMaxValue);
        onResetFilter({
            maxValue:maxValueState,
            minValue:minValueState,
            name:propertyName,
            id:propertyId
        });
    };

    return (
        <>
        <div className="flex flex-col" style={{ maxWidth: `${widthPx}px` }}
            ref={ref}
        >
            <FilterHeader
                propertyName={propertyName}
                unit={unit}
                handleReset={handleReset}
                widthPx={widthPx}
                resetFilterIds={resetFilterIds}    
            />
            <div className="flex w-full">
                {/* Min block */}
                <div className="flex flex-col items-start w-full">
                    <h1 className="
                        flex items-center text-center
                        text-itbs-annotation-small
                        font-itbs-light
                        rounded-[3px]
                    ">
                        Min
                    </h1>
                    <input className={`
                        w-full
                        bg-itbs-dirty-white
                        pl-1
                        ${redIndicatorMinState ? 'outline-[2px] outline-red-500' : ''}
                    `}
                        type="number" 
                        value={minValueState} onChange={handleMinChange}
                    />
                </div>
                {/* Gap */}
                <h1 className="
                    flex items-center text-center justify-center
                    text-itbs-annotation-small
                    font-itbs-light
                    w-[20px] flex-shrink-0
                ">
                    _
                </h1>
                {/* Max block */}
                <div className="flex flex-col items-start w-full">
                    <h1 className="
                        flex items-center text-center
                        text-itbs-annotation-small
                        font-itbs-light
                    ">
                        Max
                    </h1>
                    <input className={`
                        w-full
                        bg-itbs-dirty-white
                        rounded-[3px]
                        pl-1
                        ${redIndicatorMaxState ? 'outline-[2px] outline-red-500' : ''}
                    `} 
                        type="number" 
                        value={maxValueState} onChange={handleMaxChange} 
                    />
                </div>
            </div>
        </div>
        </>
    );
};

const RadioFilter = ({
    onResetFilter=(value, name, id) => {},
    onValueChange=(value, name, id) => {},
    ref=null,
    propertyName="<Property Name>",
    propertyId="<Property ID>",
    options=["YES", "NO", "BOTH"],
    defaultValueIndex=2,
    widthPx=-1,//if < 0 - 100%
    resetFilterIds=[]
}) => {

    const [key, setKey] = useState(1);//for radio choice to rerender to default

    const handleReset = (new_key=true) => {
        if(new_key) {
            setKey((key + 1) % 10);
        }
        const val = options[defaultValueIndex % options.length];
        onResetFilter(val, propertyName, propertyId);
    };

    return (
         <div className="flex flex-col"
            ref={ref}
         >
            <FilterHeader 
                widthPx={widthPx} 
                propertyName={propertyName} 
                handleReset={handleReset} 
                resetFilterIds={resetFilterIds}
            />
            <RadioChoice
                key={key}
                options={options}
                onValueChange={(value) => {
                    if(value === options[defaultValueIndex % options.length]) {
                        handleReset(false);
                        return;
                    }
                    onValueChange(value, propertyName, propertyId);
                }}
                defaultValueIndex={defaultValueIndex}
                widthPx={widthPx}
            />
        </div>
    );
};

const SelectorFilter = ({
    onResetFilter=(value, name, id) => {},
    onValueChange=(value, name, id) => {},
    onOpenChange=(name, id, isOpen) => {},
    ref=null,
    propertyName="<Property Name>",
    propertyId="<Property ID>",
    options=["<Option 1>", "<Option 2>", "<Option 3>"],
    defaultValueIndex=0,
    widthPx=-1,//if < 0 - 100%
    resetFilterIds=[]
}) => {

    const [key, setKey] = useState(1);//for selector to rerender

    const handleReset = (new_key=true) => {
        if(new_key) {
            setKey((key + 1) % 10);
        }
        const val = options[defaultValueIndex % options.length];
        onResetFilter(val, propertyName, propertyId);
    };

    const selectorClassName = widthPx < 0 ? "w-full h-full" : `w-full h-full max-w-[${widthPx}px]`;
    return (
         <div className="flex flex-col"
            ref={ref}
         >
            <FilterHeader 
                widthPx={widthPx} 
                propertyName={propertyName} 
                handleReset={handleReset}
                resetFilterIds={resetFilterIds}
            />
            <Selector
                key={key}
                defaultValueIndex={defaultValueIndex}
                options={options}
                onValueChange={(value) => {
                    console.log(`calling value change from filter : ${value}`)
                    if(value === options[defaultValueIndex % options.length]) {
                        handleReset(false);
                        return;
                    }
                    onValueChange(value, propertyName, propertyId);
                }}
                onOpenChange={(isOpen) => {
                    onOpenChange(propertyName, propertyId, isOpen);
                }}
                elementClassName={selectorClassName}
            />
        </div>
    );
}



export { NumberFilter, RadioFilter, SelectorFilter }