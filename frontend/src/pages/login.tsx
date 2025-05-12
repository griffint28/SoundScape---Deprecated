import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate from React Router

interface LoginResponse {
    key?: string; // if using JWT auth
    non_field_errors?: string[];
    [key: string]: any;
}

export default function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setErrors(null);

        try {
            const response = await fetch('/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Required for session auth
                body: JSON.stringify({ username, password }),
            });

            const data: LoginResponse = await response.json();

            if (!response.ok) {
                if (data.non_field_errors) {
                    setErrors(data.non_field_errors.join(' '));
                } else {
                    setErrors('Login failed. Please check your credentials.');
                }
            } else {
                // Logged in successfully
                // Optionally: redirect or update global auth state
                console.log('Logged in:', data);
                navigate('/home');
            }
        } catch (error) {
            setErrors('Something went wrong.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleLogin} className="max-w-sm mx-auto p-4 bg-white shadow rounded">
            <h2 className="text-xl font-bold mb-4">Login</h2>

            {errors && <p className="text-red-500 mb-3">{errors}</p>}

            <div className="mb-3">
                <label htmlFor="username" className="block text-sm font-medium">
                    Username
                </label>
                <input
                    type="text"
                    id="username"
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    required
                />
            </div>

            <div className="mb-4">
                <label htmlFor="password" className="block text-sm font-medium">
                    Password
                </label>
                <input
                    type="password"
                    id="password"
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                />
            </div>

            <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
            >
                {isLoading ? 'Logging in...' : 'Login'}
            </button>
        </form>
    );
}
