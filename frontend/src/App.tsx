import { useEffect, useState } from "react";

import Login from './pages/login';
import Signup from './pages/signup';
import Dashboard from './pages/dashboard.tsx';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from "./pages/home.tsx";

function App() {
    const [data, setData] = useState<{ message: string; items: string[] } | null>(null);

    useEffect(() => {
        fetch("api/data/")
            .then((res) => res.json())
            .then(setData)
            .catch((err) => console.error("Fetch error:", err));
    }, []);

    if (!data) return <div>Loading...</div>;

    return (
        <div className="p-6 font-sans">
            <h1 className="text-2xl font-bold mb-4">{data.message}</h1>
            <ul className="list-disc pl-5">
                {data.items.map((item, i) => (
                    <li key={i} className="text-gray-700">{item}</li>
                ))}
            </ul>
            <Router>
                <nav>
                    <Link to="/login">Login</Link>
                    <Link to="/signup">Register</Link>
                </nav>
                <Routes>
                    <Route path="/login" element={<Login/>} />
                    <Route path="/signup" element={<Signup/>} />
                    <Route path="/home" element={<Home />} />
                    <Route path="/dashboard"  element={<Dashboard />} />
                </Routes>
            </Router>
        </div>
    );
}

export default App;
