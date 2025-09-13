import React, { useState } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";

function formatNumber(value) {
  const [intPart, decimalPart] = value.toString().split(".");
  const spacedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return decimalPart !== undefined ? `${spacedInt}.${decimalPart}` : spacedInt;
}


const BoolProperty = ({
    name="<Bool Property>", 
    value=true,
    widthPx=-1,//< 0 - full width
    variant="main"//"main", "secondary"
}) => {
    const textVariant = variant === "main" ? "text-itbs-usual-small font-itbs-bold" : "text-itbs-annotation-small";
    const sizeVariant = variant === "main" ? 24 : 20;
    return (
        <div className="flex items-center justify-between w-full overflow-hidden gap-5" style={{ maxWidth: `${widthPx}px` }}>

            <h1 className={`flex flex-1 break-words break-all text-left text-itbs-usual-small line-clamp-3 ${textVariant}`} style={{ maxWidth: `${widthPx - sizeVariant}px` }}>
                {name}
            </h1>
            <div className="flex items-center">

            {value ? (
                <ResizableAsset asset_from_assets={assets.icons.MarkGreen} w={sizeVariant} h={sizeVariant} />
            ) : (
                <ResizableAsset asset_from_assets={assets.icons.CrossRed} w={sizeVariant} h={sizeVariant} />
            )}
            </div>
        </div>
    );
};


const NumberProperty = ({
    name="<Number Property>",
    value=10000000.12,
    unit="?",
    widthPx=-1,//< 0 - full width
    variant="main"//"main", "secondary"
}) => {
    const textVariant = variant === "main" ? "text-itbs-usual-small font-itbs-bold" : "text-itbs-annotation-small";
    return (
        <div className="flex items-center justify-between w-full overflow-hidden gap-5" style={{ maxWidth: `${widthPx}px` }}>

            <h1 className={`flex-1 break-words text-left ellipsis line-clamp-3 ${textVariant}`}>
                {name}
            </h1>
            <h1 className={`break-words text-right ellipsis line-clamp-3 text-itbs-dark-blue`}>
                {formatNumber(value)} {unit}
            </h1>
        </div>
    );
};

const EnumProperty = ({
    name="<Enum Property>",
    options=["<Option 1>", "<Option 2>", "<Option 3>"],
    widthPx=-1,//< 0 - full width
    variant="main"//"main", "secondary"
}) => {
    const textVariant = variant === "main" ? "text-itbs-usual-small font-itbs-bold" : "text-itbs-annotation-small";
    const sizeVariant = variant === "main" ? 24 : 20;
    return (
        <div className="flex flex-wrap items-start justify-between w-full overflow-hidden gap-5" style={{ maxWidth: `${widthPx}px` }}>

            <h1 className={`flex-2 break-words text-left ellipsis line-clamp-3 ${textVariant}`}>
                {name}
            </h1>
            <div className="flex-1 flex-col items-end justify-between gap-[5px]">
                {options.map((option, index) => (
                    <h1 className={`break-words 
                        text-right ellipsis line-clamp-3 
                        text-itbs-usual-small text-itbs-dark-red
                        border-[1px] rounded-[7px] py-[2px] px-[3px] 
                        border-itbs-light-gray
                        hover:bg-itbs-light-orange
                    `} key={index}>
                        {option}
                    </h1>
                ))}
            </div>
        </div>
    );
};


export { BoolProperty, NumberProperty, EnumProperty }