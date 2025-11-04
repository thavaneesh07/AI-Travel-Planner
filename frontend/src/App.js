import React from "react";
import Chatbot from "./components/Chatbot";

function App() {
  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#f9f9f9",
      display: "flex",
      justifyContent: "center",
      alignItems: "flex-start",
      paddingTop: "50px"
    }}>
      <div style={{
        width: "600px",
        background: "white",
        borderRadius: "10px",
        boxShadow: "0 0 10px rgba(0,0,0,0.1)",
        padding: "20px"
      }}>
        <Chatbot />
      </div>
    </div>
  );
}

export default App;
