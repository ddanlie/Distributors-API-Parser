import React, { useState, useEffect } from 'react';
import ItemCard from "@/components/item_card";
import Selector from "@/components/selector";
import Sign from "@/components/sign";
import { RemovableWord, RemovableWordList } from "@/components/removable";
import { RadioChoice } from "@/components/choice";
import { RadioFilter, NumberFilter, SelectorFilter, resetFilterAtomFamily } from "@/components/filters";
import Button from "@/components/buttons";
import { BoolProperty, NumberProperty, EnumProperty } from "@/components/properties";

import { useSetAtom } from "jotai";

const ComponentsDemo = () => {
    const setResetSignalForDefault = useSetAtom(resetFilterAtomFamily("default"));

    return (
        <div>
        <h1>Components Demo</h1>
        <br/>
        <h1>Items:</h1>
        <ItemCard name="asdsadsasaddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"/>
        <ItemCard/>
        <ItemCard/>
        <ItemCard/>
        <ItemCard/>
        <br/>
        <h1>Selector:</h1>
        <Selector defaultValue={"TREOLAN"} variant="client-filter"/>
        <Selector/>
        <Sign isActive={true}/>
        <Sign isActive={false}/> 

        <RemovableWordList words={["<Keyword 1>", "<Keyword 2>adsasdadsadsadsadadasdsasdadsa", "<Keyword 3>"]}></RemovableWordList>

        <RadioChoice onValueChange={(index)=>{console.log(`Selected: ${index}`)}}></RadioChoice>

        <NumberFilter widthPx={200} resetFilterId={"default"}></ NumberFilter>
        <RadioFilter widthPx={200} resetFilterId={"default"} defaultValue={"YES"}></RadioFilter>
        <SelectorFilter widthPx={200} resetFilterId={"default"} ></SelectorFilter>

        <button onClick={() => {
            setResetSignalForDefault(true);
        }}>
            Reset All
        </button>

        <br></br>
        <div className="flex justify-center gap-5">
        <Button text={"Hello, World!"} disabled={true}/>
        <Button text={"Hello, World!"} variant="support" disabled={false} />
        <Button text={"Hello, World!"} variant="support" disabled={true} />
        <Button text={"Hello, World!"} variant="main" subVariant="classic"/>
        <Button text={"Hello"} variant="main" subVariant="danger"/>
        </div>
        <br></br>
        <div className="flex flex-col items-center gap-5">
            <BoolProperty name="Is Actadadasadadasdsadsadsadasadasdsadasive" widthPx={200} value={true} />
            <BoolProperty name="Is Active" widthPx={200} variant="secondary" value={false} />
            <NumberProperty name="Age asdsada d asd a dasdsadaadsdad" widthPx={300}/>
            <EnumProperty name="Statassadsadasdsadadsadsadsadsadsadsadadsadasdsadus" widthPx={300} value={"active"} options={["activesadssadsadsad", "inactive", "pe"]} />
            <BoolProperty name="Is Active" widthPx={200} variant="secondary" value={false} />
        </div>


        </div>
    );
};

export default ComponentsDemo;