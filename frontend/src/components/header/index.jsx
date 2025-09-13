import React, { useState } from 'react';
import { atom, useAtom } from 'jotai';
import { useNavigate } from "react-router-dom";


const selectedTabAtom = atom("search");

const Header = ({}) => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useAtom(selectedTabAtom);

  const selectedTabStyle = `
    shadow-[0_2px_0_0_white]
  `;

  const textStyle = `
    font-itbs_default 
    text-itbs_subtitle_small
    text-white
    hover:shadow-[0_2px_0_0_white]
    hover:cursor-pointer
  `;

  return (
    <div className="flex bg-[#40829B]">
      <div className="
        flex 
        h-[80px]
        w-full
        items-center 
        justify-center
        gap-8 
      ">
        <nav onClick={() => {
          setSelectedTab("compare");
          navigate("/compare")
        }}>
          <h1 className={`
            ${textStyle} 
            ${selectedTab === "compare" && selectedTabStyle}
          `}>
            Compare
          </h1>
        </nav>
        <nav onClick={() => {
          setSelectedTab("search");
          navigate("/search")
        }}>
          <h1 className={`
            ${textStyle} 
            ${selectedTab === "search" && selectedTabStyle}
          `}>
            Search
          </h1>
        </nav>
        <nav onClick={() => {
          setSelectedTab("documents");
          navigate("/documents")
        }}>
          <h1 className={`
            ${textStyle} 
            ${selectedTab === "documents" && selectedTabStyle}
          `}>
            Documents
          </h1>
        </nav>
      </div>
    </div>
  );
}

export default Header;