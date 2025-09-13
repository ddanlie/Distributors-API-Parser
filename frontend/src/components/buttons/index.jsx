import React, { useEffect, useState, useId } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";



const Button = ({
    onClick=() => {},
    text="Button",
    disabled=false,
    type="button",
    variant="main",//"main", "support", "custom"
    subVariant="neutral",//"neutral", "danger", "classic"
    customClassName="",//used for "custom" variant
    children=null//used for "custom" variant
}) => {

    const variantClassMap = 
    {
        general: {
            "main"   : "hover:cursor-pointer rounded-[7px] p-[7px] text-center hover:ring-1 hover:ring-itbs-dark-black active:relative active:top-[5px]",
            "support": "hover:cursor-pointer rounded-[5px] p-[5px] text-center hover:ring-1 hover:ring-itbs-dark-black active:relative active:top-[3px]",
        },
        border: {
            "neutral": "",
            "danger" : "",
            "classic": "border-[2px] border-black",
        },
        text: {
            "main": {
                "neutral": "text-white text-itbs-subtitle-small",
                "danger" : "text-white text-itbs-subtitle-small",
                "classic": "text-black text-itbs-subtitle-small",
            },
            "support": {
                "neutral": "text-white text-itbs-annotation-small",
                "danger" : "text-white text-itbs-annotation-small",
                "classic": "text-black text-itbs-annotation-small",
            }
        },
        size: {
            "main": {
                "neutral": "w-fit h-[44px] min-h-[44px] max-h-[44px]",
                "danger" : "w-fit h-[44px] min-h-[44px] max-h-[44px]",
                "classic": "w-fit h-[44px] min-h-[44px] max-h-[44px]",
            },
            "support": {
                "neutral": "w-fit h-[44px] min-h-[35px] max-h-[35px]",
                "danger" : "w-fit h-[44px] min-h-[35px] max-h-[35px]",
                "classic": "w-fit h-[44px] min-h-[35px] max-h-[35px]",
            }
        },
        bgColor: {
            "neutral": "bg-itbs-light-blue",
            "danger" : "bg-itbs-dark-red",
            "classic": "bg-white",
        },
        disabledStyle: {
            "neutral": "disabled:text-itbs-light-gray disabled:bg-itbs-dirty-white disabled:ring-itbs-light-black",
            "danger" : "disabled:text-itbs-light-gray disabled:bg-itbs-dirty-white disabled:ring-itbs-light-black",
            "classic": "disabled:text-itbs-light-gray disabled:bg-itbs-dirty-white disabled:ring-itbs-light-black",
        },
    }

    const finalStyle = `
        ${variantClassMap.general[variant]} 
        ${variantClassMap.text[variant][subVariant]} 
        ${variantClassMap.size[variant][subVariant]}
        ${variantClassMap.border[subVariant]} 
        ${variantClassMap.bgColor[subVariant]} 
        ${disabled ? variantClassMap.disabledStyle[subVariant] : ''}
    `;

    return (
        variant === "custom" ? (
            <button onClick={onClick} disabled={disabled} type={type} className={customClassName}>
                {children}
            </button>
        ) : (
            <button onClick={onClick} disabled={disabled} type={type} className={finalStyle}>
                {text}
            </button>
        )
    );
};


export default Button;