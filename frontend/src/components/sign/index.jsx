import React, { useState } from 'react';
import assets, { ResizableAsset } from "@/toolbox/utils/assets/importAllAssets.jsx";

const Sign = ({
  text="<Sign>",
  isActive=false,
  onClick=(isActive) => {},
  panelClassName=""
}) => {
  const [isActiveState, setIsActiveState] = useState(isActive);

  const bgStatus = isActiveState ? "bg-itbs-light-orange" : "bg-itbs-light-black";

  return (
    <div className={`
      ${panelClassName} 
      ${bgStatus}  
      flex items-center justify-around 
      w-fit
      max-w-[230px] max-h-[35px]
      rounded-[7px]
      p-[10px]
      hover:cursor-pointer
    `}
      onClick={()=>{
        onClick(!isActiveState);
        setIsActiveState(!isActiveState);
      }}
    >
      <h1 className={`text-itbs-annotation-small text-center truncate`}>
        {text}
      </h1>
    </div>
  );
};

export default Sign;