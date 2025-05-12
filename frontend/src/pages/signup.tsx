import { useState } from 'react';

interface RegisterResponse {
    key?: string; // only if using JWT
    [key: string]: string[] | string | undefined;
}

export default function RegisterForm() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [errors, setErrors] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors(null);
        setIsLoading(true);

        try {
            const response = await fetch('/api/auth/registration/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include', // if you're using session auth
                body: JSON.stringify({
                    username,
                    email,
                    password1,
                    password2,
                }),
            });

            const data: RegisterResponse = await response.json();

            if (!response.ok) {
                const firstError = Object.entries(data)
                    .map(([field, msg]) => `${field}: ${(msg as string[]).join(', ')}`)
                    .join(' | ');
                setErrors(firstError || 'Registration failed.');
            } else {
                // Registration success
                console.log('Registered:', data);
            }
        } catch (err) {
            setErrors('Something went wrong.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleRegister} className="max-w-sm mx-auto p-4 bg-white shadow rounded">
            <h2 className="text-xl font-bold mb-4">Register</h2>

            {errors && <p className="text-red-500 mb-3">{errors}</p>}

            <div className="mb-3">
                <label className="block text-sm font-medium">Username</label>
                <input
                    type="text"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    required
                />
            </div>

            <div className="mb-3">
                <label className="block text-sm font-medium">Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    required
                />
            </div>

            <div className="mb-3">
                <label className="block text-sm font-medium">Password</label>
                <input
                    type="password"
                    value={password1}
                    onChange={e => setPassword1(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    required
                />
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium">Confirm Password</label>
                <input
                    type="password"
                    value={password2}
                    onChange={e => setPassword2(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded p-2"
                    required
                />
            </div>

            <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700"
            >
                {isLoading ? 'Registering...' : 'Register'}
            </button>
        </form>
    );
}
