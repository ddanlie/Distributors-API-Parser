import React from 'react';

import CrossRed from "@/assets/icons/CrossRed.svg";
import MarkGreen from "@/assets/icons/MarkGreen.svg";

import CompareDocsActive from "@/assets/interactives/CompareDocsActive.svg";
import CompareDocsInactive from "@/assets/interactives/CompareDocsInactive.svg";
import AddPropertyActive from "@/assets/interactives/AddPropertyActive.svg";
import AddPropertyInactive from "@/assets/interactives/AddPropertyInactive.svg";
import ArrowDown from "@/assets/interactives/ArrowDown.svg";
import ArrowUp from "@/assets/interactives/ArrowUp.svg";
import ArrowLeft from "@/assets/interactives/ArrowLeft.svg";
import ArrowRight from "@/assets/interactives/ArrowRight.svg";
import DeleteSomething from "@/assets/interactives/DeleteSomething.svg";
import Restart from "@/assets/interactives/Restart.svg";
import SaveDocActive from "@/assets/interactives/SaveDocActive.svg";
import SaveDocInactive from "@/assets/interactives/SaveDocInactive.svg";


const assets_img = {
  interactives: {
    CompareDocsActive  : <img src = {CompareDocsActive} alt   = "icon" className="hover:cursor-pointer"/>,
    CompareDocsInactive: <img src = {CompareDocsInactive} alt = "icon" className="hover:cursor-pointer"/>,
    AddPropertyActive  : <img src = {AddPropertyActive} alt   = "icon" className="hover:cursor-pointer"/>,
    AddPropertyInactive: <img src = {AddPropertyInactive} alt = "icon" className="hover:cursor-pointer"/>,
    ArrowDown          : <img src = {ArrowDown} alt           = "icon" className="hover:cursor-pointer"/>,
    ArrowUp            : <img src = {ArrowDown} alt           = "icon" className="hover:cursor-pointer"/>,
    ArrowLeft          : <img src = {ArrowLeft} alt           = "icon" className="hover:cursor-pointer"/>,
    ArrowRight         : <img src = {ArrowRight} alt          = "icon" className="hover:cursor-pointer"/>,
    DeleteSomething    : <img src = {DeleteSomething} alt     = "icon" className="hover:cursor-pointer"/>,
    Restart            : <img src = {Restart} alt             = "icon" className="hover:cursor-pointer"/>,
    SaveDocActive      : <img src = {SaveDocActive} alt       = "icon" className="hover:cursor-pointer"/>,
    SaveDocInactive    : <img src = {SaveDocInactive} alt     = "icon" className="hover:cursor-pointer"/>,
  },
  icons: {
    CrossRed : <img src = {CrossRed} alt  = "icon"/>,
    MarkGreen: <img src = {MarkGreen} alt = "icon"/>,
  },
};

const assets = {
  interactives: {
    CompareDocsActive,  
    CompareDocsInactive,
    AddPropertyActive,  
    AddPropertyInactive,
    ArrowDown,   
    ArrowUp,       
    ArrowLeft,          
    ArrowRight,         
    DeleteSomething,    
    Restart,            
    SaveDocActive,      
    SaveDocInactive    
  },
  icons: {
    CrossRed,
    MarkGreen
  }
};

const ResizableAsset = ({
  asset_from_assets=assets.interactives.ArrowUp,
  w=24,
  h=24,
}) => {

  return (
    <img 
      src={asset_from_assets} 
      alt="icon" 
      className="hover:cursor-pointer" 
      style={{ width: `${w}px`, height: `${h}px` }} 
    />
  );

};

export {ResizableAsset, assets_img}
export default assets;