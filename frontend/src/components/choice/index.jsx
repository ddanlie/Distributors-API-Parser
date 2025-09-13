import React, { useEffect, useState, useId } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";



const CheckBoxChoice = () => {
    return (
        <div>
            <h1>CheckBox Choice is not implemented</h1>
        </div>
    );
};



const RadioChoice = ({
    options=["AND", "OR", "BOTH"],
    onValueChange=(option) => {},
    widthPx=-1,//if -1 - 100%
    defaultValueIndex=2
}) => {
    const name = useId();
    const [selectedValue, setSelectedValue] = useState(null);

    useEffect(() => {
        setSelectedValue(options[defaultValueIndex % options.length]);
        onValueChange(options[defaultValueIndex % options.length]);
    }, []);

    return (
        <div className="flex flex-wrap gap-[7px] w-full" style={{ maxWidth: `${widthPx}px` }}>
            {options.map((option, index) => (
                <div key={index} className="flex items-center gap-1">
                    <input
                        type="radio" 
                        id={`${name}-${index}`} 
                        name={`${name}-${index}`}
                        checked={selectedValue === option}
                        onChange={() => {
                            setSelectedValue(option);
                            onValueChange(option);
                        }}
                    />
                    <label className="text-itbs-annotation-small" htmlFor={`${name}-${index}`}>{option}</label>
                </div>
            ))}
        </div>
    );
};


export { CheckBoxChoice, RadioChoice }