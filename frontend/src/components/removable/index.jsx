// ################################################# IMPORTANT #################################################
// Make sure all parents of RemovableWordList and RemovableWord have "OVERFLOW-X-VISIBLE"

import React, { useState } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";

const Removable = ({
  onRemove=() => {},
  children=<></>
}) => {

  return (
    <div className={`
        flex justify-between items-center gap-1 w-fit h-fit overflow-x-visible
    `}> 
        <div className="flex overflow-x-visible">
            {children}
        </div>
        <div className={`
            flex flex-col items-start
            hover:cursor-pointer
            h-full
        `} 
            onClick={() => {onRemove()}}
        >
            <ResizableAsset asset_from_assets={assets.interactives.DeleteSomething} w={12} h={12} />
        </div>
    </div>
  );
};

// ################################################# IMPORTANT #################################################
// Make sure all parents of this have "OVERFLOW-X-VISIBLE"
const RemovableWord = ({
    text="<Keyword>",
    onRemove=() => {},
    textClassName="text-black"
}) => {
  return ( 
    <Removable onRemove={onRemove}>
        <div className="flex relative overflow-visible">
            <h1 className={`
                ${textClassName}
                max-w-[200px] px-2 py-0.5 z-20
                truncate text-itbs-annotation-small 
                rounded-[7px]
                hover:cursor-default
                hover:max-w-full
                relative inset-0

            `}>
                {text}
            </h1>
            {/* cover half text so its not hoverable */}
            <div className="
                absolute left-1/2 inset-y-0
                hover:
                bg-black opacity-0
                h-full w-[50%] z-30
            ">
            </div>
        </div>
    </Removable>
  );
};

// ################################################# IMPORTANT #################################################
// Sorry, its not scrollable, just expandable. 
// Make sure all parents of this have "OVERFLOW-X-VISIBLE"
const RemovableWordList = ({
    children = <>
            <RemovableWord key={0} text="abc" textClassName='bg-blue-500'/>
            <RemovableWord key={1} text="sddasdsasdadsadsadsadsadsadsadsadsadsadadasdasds" textClassName='bg-blue-500'/>
            <RemovableWord key={2} text="sddasdasds" textClassName='bg-blue-500'/>
            <RemovableWord key={3} textClassName='bg-blue-500'/>
        </>,//not used if words are present
    words=[], // no need to create children list if this is present, default RemovableWord will be used
    useChildren=false,
    onRemove=(wordIndex) => {}, //used if words are present 
    onRemoveAll=() => {}, //used if words are present
    textClassName="text-black", //used if words are present
    listClassName="gap-2 bg-transparent max-w-[250px]"
}) => {
    return (
        useChildren ? (
            <div className="flex flex-col gap-[20px] w-fit">
                <div className={`flex flex-wrap overflow-visible ${listClassName}`}>
                    {children}
                </div>

                <h1 className="
                    text-itbs-annotation-small font-itbs-light
                    hover:cursor-pointer
                    w-full text-right
                "
                    onClick={() => onRemoveAll()}
                >
                    Clear All
                </h1>
            </div>
        ) : (
            <div className="flex flex-col gap-[20px] w-full">
                <div className={`flex flex-wrap overflow-visible ${listClassName}`}>
                    {words.map((word, index) => (
                        <RemovableWord 
                        key={index} 
                        text={word} 
                        textClassName={textClassName}
                        onRemove={() => {onRemove(index)}}
                        />
                    ))}
                </div>
                <div className="flex w-full items-end">
                    <h1 className="
                        text-itbs-annotation-small font-itbs-light
                        hover:cursor-pointer
                        w-full text-right
                    "
                        onClick={() => onRemoveAll()}
                    >
                        Clear All
                    </h1>
                </div>
            </div>
        )
    );
};

export { RemovableWord, RemovableWordList }
export default Removable;
