import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";

const DevComponent = ({}) => {
  const navigate = useNavigate();

  const selectedTabStyle = `
    shadow-[0_2px_0_0_white]
  `;

  const textStyle = `
    font-itbs_default 
    text-itbs_subtitle_small
    text-white
    
    hover:shadow-[0_1px_0_0_white]
  `;

  return (
    <div className="bg-[#40829B]">
      <div className="
        h-[80px]
        flex 
        items-center 
        justify-center
        gap-4  
      ">
        <nav onClick={() => navigate("/compare")}>
          <h1 className={textStyle}>Compare</h1>
        </nav>
        <nav onClick={() => navigate("/search")}>
          <h1 className={textStyle}>Search</h1>
        </nav>
        <nav onClick={() => navigate("/documents")}>
          <h1 className={textStyle}>Documents</h1>
        </nav>
      </div>
    </div>
  );
}

export default DevComponent;