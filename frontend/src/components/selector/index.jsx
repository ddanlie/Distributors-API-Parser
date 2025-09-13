import React, { useState, useMemo } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";

const Selector = ({
    defaultValueIndex=0,
    options=["<Default Value>", "<Option 1>", "<Option 2>", "<Option 3>"],
    onValueChange=(value) => {},
    onOpenChange=(isOpen) => {},
    variant="search-mode", //"client-filter", "search-mode", "custom".
    reverseArrow=false,
    optionTextClassName="",
    elementClassName=""
}) => {
    const [selectedValue, setSelectedValue] = useState(options[defaultValueIndex % options.length]);
    const [isOpened, setIsOpened] = useState(false);

    const variantClassMap = {
        useOptions: {
            "search-mode": true,
            "client-filter": false,
            "custom": true,
        },
        element: {
            "custom": elementClassName,
            "search-mode": " bg-itbs-light-blue rounded-[3px] px-[6px] w-[145px] h-[20px] min-w-[145px] min-h-[20px] max-w-[145px] max-h-[20px] ",
            "client-filter": " bg-itbs-light-orange rounded-[7px] px-[8px] w-[216px] h-[40px] min-w-[216px] min-h-[40px] max-w-[216px] max-h-[40px] ",
        },
        text: {
            "custom": optionTextClassName,
            "search-mode": " text-itbs-annotation-small ",
            "client-filter": " text-itbs-subtitle-small ",
        },
        arrowDown: {
            "search-mode": <ResizableAsset asset_from_assets={assets.interactives.ArrowDown} w={15} h={15} />,
            "client-filter": <ResizableAsset asset_from_assets={assets.interactives.ArrowDown} w={30} h={30} />,
        },
        arrowUp: {
            "search-mode": <ResizableAsset asset_from_assets={assets.interactives.ArrowUp} w={15} h={15} />,
            "client-filter": <ResizableAsset asset_from_assets={assets.interactives.ArrowUp} w={30} h={30} />,
        }
    };

    const finalArrow = useMemo(() => {
        let val = isOpened;
        if (reverseArrow) {
            val = !val;
        }
        if (val) {
            return variantClassMap.arrowDown[variant] || variantClassMap.arrowUp["search-mode"];
        }
        else {
            return variantClassMap.arrowUp[variant] || variantClassMap.arrowUp["search-mode"];
        }
    }, [isOpened, variant]);

    return (
        <div className={`
            flex items-center justify-between gap-2
            hover:cursor-pointer
            ${variantClassMap.element[variant] || " bg-white "}
            ${elementClassName || ""}
        `}
        >
            {variantClassMap.useOptions[variant] ? (
                <select className={`
                    ${variantClassMap.text[variant] || optionTextClassName}
                    w-full
                    h-full
                    truncate
                `}
                    id={crypto.randomUUID()}
                    name=""
                    value={selectedValue}
                    onChange={(e) => {
                        console.log(`calling on value change from selector : ${e.currentTarget.value} `);
                        setSelectedValue(e.currentTarget.value);
                        onValueChange(e.currentTarget.value);
                        setIsOpened(false);
                        onOpenChange(false);
                    }}
                    onClick={() => {
                        setIsOpened(!isOpened);
                        onOpenChange(!isOpened);
                    }}
                >
                    {options.map((option, index) => (
                        <option className={
                            `${variantClassMap.text[variant] || ""}
                            ${variantClassMap.text[variant] || optionTextClassName}
                            w-full text-left
                            line-clamp-2
                        `}
                            key={index} value={option}             
                        >
                            {option}
                        </option>
                    ))}
                </select>
            ) : (
                <div className={`
                    ${variantClassMap.text[variant] || optionTextClassName}
                    w-full
                    h-full
                    -mb-2
                    truncate
                `}
                    onClick={() => {
                        setIsOpened(!isOpened)
                        onOpenChange(!isOpened);
                        onValueChange(!isOpened);
                    }}
                >
                    {options[defaultValueIndex % options.length]}
                </div>
            )}
            <div className="hover:cursor-pointer"
                onClick={(e) => {
                    e.preventDefault();
                    setIsOpened(!isOpened);
                    onOpenChange(!isOpened);
                }}
            >
                {finalArrow}
            </div>
        </div>
    );
}

export default Selector;