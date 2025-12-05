import React from "react";
import Sidebar from "./Sidebar";
import "./Layout.css";

const Layout = ({ activeTab, setActiveTab, children }) => {
  return (
    <div className="App">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-wrapper">{children}</main>
    </div>
  );
};

export default Layout;
