import React from "react";

const Home: React.FC = () => {
    return (
        <div style={{textAlign: "center", padding: "2rem"}}>
            <h1>Welcome to the Homepage</h1>
            <p>This is a simple homepage built with React and TypeScript!</p>
            <button
                style={{
                    padding: "0.5rem 1rem",
                    background: "#007BFF",
                    color: "#fff",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                }}
                onClick={() => alert("Button clicked!")}
            >
                Click Me
            </button>
        </div>
    );
};

export default Home;