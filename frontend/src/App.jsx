//@ doesn't work here, sry

import React, { useState } from 'react'
import { Link } from "react-router-dom";
import { HashRouter, Routes, Route } from "react-router-dom";

import DefaultPageLayout from "./components/layouts";
import SearchPage from './components/pages/search';
import ComponentsDemo from './components/pages/components_demo';
// import DocumentsPage from './components/pages/documents';
// import ComparePage from './components/pages/compare';

const Compare = () => {
  return (
    <div>
      <h1>Compare</h1>
    </div>
  );
};

const Documents = () => {
  return (
    <div>
      <h1>Documents</h1>
    </div>
  );
};

function App() {

  return (
    <>
      <HashRouter>
        <Routes>
          <Route 
            path="/compare"   
            element={
              <DefaultPageLayout>
                <Compare />
              </DefaultPageLayout>
            } 
          />
          <Route 
            path="/"
            element={
              <DefaultPageLayout>
                <SearchPage /> 
                {/* <ComponentsDemo */}
              </DefaultPageLayout>
            }
          />
          <Route 
            path="/search"
            element={
              <DefaultPageLayout>
                <SearchPage />
                {/* <ComponentsDemo/> */}
              </DefaultPageLayout>
            }
          />
          <Route 
            path="/documents" 
            element={
              <DefaultPageLayout>
                <Documents />
              </DefaultPageLayout>
            }
          />
        </Routes>
      </HashRouter>
    </>
  )
}

export default App