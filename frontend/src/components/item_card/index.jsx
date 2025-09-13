import React, { useState } from 'react';
import assets, {assets_img} from "@/toolbox/utils/assets/importAllAssets.jsx";

const ItemCard = ({
    name="<Item Name>",
    description="<Item Description>",
    distributor="<Item Distributor>",
    imageSrc="<Item Image>",
    priceInfo={price:0, unit:"RUB"},
    orderInfo={minQuantity:0, unit: "pcs"},
    isFocused=false,
    interactiveCompareDocsIsActive=false,
    interactiveCompareDocsOnClick=(isActive) => {},
    interactiveSaveDocIsActive=false,
    interactiveSaveDocOnClick=(isActive) => {},
    customBg="bg-white"//really special property for additional indicators
}) => {

  const [isCompareDocsActive, setIsCompareDocsActive] = useState(interactiveCompareDocsIsActive);
  const [isSaveDocActive, setIsSaveDocActive] = useState(interactiveSaveDocIsActive);

  return (
    <div className={`
        flex items-center gap-4
        min-w-0
        w-full
        rounded-[10px]
        ${customBg ? customBg : "bg-white"}
    `}>
        {/* interactive icons */}
        <div className="
            flex flex-col items-center justify-end 
            gap-1 -space-x-3 pb-3
            h-full min-w-[40px] min-h-[40px]
        ">
            <div className="hover:cursor-pointer" 
                onClick={() => {
                    setIsCompareDocsActive(!isCompareDocsActive);
                    interactiveCompareDocsOnClick(!isCompareDocsActive)
                }}
            >
                {
                    isCompareDocsActive ? 
                    assets_img.interactives.CompareDocsActive : 
                    assets_img.interactives.CompareDocsInactive
                }
            </div>
            <div className="hover:cursor-pointer" 
                onClick={() => {
                    setIsSaveDocActive(!isSaveDocActive);
                    interactiveSaveDocOnClick(!isSaveDocActive)
                }} 
            >
                {
                    isSaveDocActive ? 
                    assets_img.interactives.SaveDocActive : 
                    assets_img.interactives.SaveDocInactive
                }
            </div>
        </div>
        {/* item */}
        <div className="
            flex flex-col justify-between items-start w-full
        ">
            {/* distributor */}
            <h1 className="
                font-itbs-bold
                text-itbs-dark-orange
                text-itbs-usual-text-small
                w-full
                text-left
            ">
                {distributor}
            </h1>
            {/* item info */}
            <div className={`
                flex items-start px-2 py-4 gap-2
                ${isFocused ? "bg-white ring-1 ring-itbs-dark-gray" : "bg-itbs-white-blue"}
                rounded-[10px] 
                hover:cursor-pointer
                w-full
            `}>
                {/* item image */}
                <img className="
                    min-w-[64px] min-h-[64px] rounded-[5px]
                    bg-white
                "
                    src={imageSrc || null} alt="Item" 
                />
                
                
                {/* item name, description */}
                <div className="
                    flex flex-col flex-1 justify-around items-start 
                    h-full min-w-[40px] min-h-[40px]
                    ">
                    {/* font-itbs-bold */}
                    <h1 className="
                        text-itbs-usual-small
                        break-all
                        break-words
                        text-left
                        line-clamp-1
                    ">
                        {name}
                    </h1>
                    <h1 className="
                        text-itbs-annotation-small
                        break-all
                        break-words
                        text-left
                        line-clamp-2
                    ">
                        {description}
                        {/* Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras congue, arcu at luctus facilisis, lorem ligula ornare felis, non feugiat lacus magna vel libero. Praesent ut dui elit. Praesent condimentum ornare erat, ac faucibus nulla semper id. Pellentesque at ante sed elit dapibus placerat volutpat in mi. In commodo congue diam nec laoreet. Praesent at rhoncus metus. Curabitur libero massa, sollicitudin sed orci eget, pharetra commodo ante. Nam nec tempor elit. */}
                    </h1>
                </div>
                {/* item price, order info */}
                <div className="
                    flex flex-col justify-around items-end 
                    h-full min-w-[80px]
                ">
                    {/* price */}
                    <h1 className="
                        text-itbs-usual-small
                        text-right
                    ">
                        {priceInfo.price} {priceInfo.unit}
                    </h1>

                    {/* order */}
                    <h1 className="
                        text-itbs-dark-orange
                        text-itbs-annotation-small
                        break-words
                        text-right
                        line-clamp-2
                    ">
                        Min order:
                        <br/>
                        {orderInfo.minQuantity} {orderInfo.unit}
                    </h1>
                </div>
            </div>
        </div>
    </div>
  );
};

export default ItemCard;

