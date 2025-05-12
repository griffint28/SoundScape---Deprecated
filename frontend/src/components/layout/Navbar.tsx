import React, {useState} from "react";

const Navbar: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(true);

    const toggleNavbar = () => {
        setIsCollapsed(!isCollapsed);
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <button className="navbar-toggle" onClick={toggleNavbar}>
                    {isCollapsed ? "☰" : "✕"}
                </button>
                <ul className={`navbar-menu ${isCollapsed ? "collapsed" : ""}`}>
                    <li className="navbar-item">
                        <a href="#home" className="navbar-link">Home</a>
                    </li>
                    <li className="navbar-item">
                        <a href="#spotify" className="navbar-link">Song Search</a>
                    </li>
                    <li className="navbar-item">
                        <a href="#top-tracks" className="navbar-link">Personal Song Statistics</a>
                    </li>
                    <li className="navbar-item">
                        <a href="#top-artists" className="navbar-link">Personal Artists Statistics</a>
                    </li>
                    <li className="navbar-item">
                        <a href="#jokes" className="navbar-link">Personal Jokes</a>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;