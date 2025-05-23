import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Lock, User, Mail, CheckCircle } from 'lucide-react'; // Import icons

const RegistrationForm = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('/api/auth/registration/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, email, password1: password, password2: confirmPassword }),
            });

            const data = await response.json();

            if (response.ok) {
                console.log('Registration successful!', data);
                setSuccess(true);
                window.location.href = '/api/spotify-login';
            } else {
                let errorMessage = 'Registration failed.';
                if (data && data.non_field_errors) {
                    errorMessage = data.non_field_errors.join(' ');
                } else if (data && data.detail) {
                    errorMessage = data.detail;
                }
                setError(errorMessage);
            }
        } catch (err: any) {
            setError(err.message || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const formVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeInOut' } },
    };

    const inputVariants = {
        hidden: { opacity: 0, x: -20 },
        visible: { opacity: 1, x: 0, transition: { duration: 0.4, delay: 0.2 } },
    };

    const buttonVariants = {
        hover: { scale: 1.05 },
        tap: { scale: 0.95 },
    };

    // Success message content
    if (success) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, ease: 'easeInOut' }}
                    className="bg-white/5 backdrop-blur-md rounded-xl shadow-2xl p-8 w-full max-w-md border border-white/10 text-center"
                >
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-semibold text-white mb-2">Registration Successful!</h2>
                    <p className="text-gray-400 mb-6">
                        Your account has been created. Please check your email to confirm your registration.
                    </p>
                    <a
                        href="/login" // Adjust the URL as needed
                        className="inline-block bg-gradient-to-r from-purple-500 to-blue-500 text-white px-6 py-2 rounded-full hover:scale-105 transition-all duration-200"
                    >
                        Go to Login
                    </a>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black flex items-center justify-center p-4">
            <motion.div
                variants={formVariants}
                initial="hidden"
                animate="visible"
                className="bg-white/5 backdrop-blur-md rounded-xl shadow-2xl p-8 w-full max-w-md border border-white/10"
            >
                <h1 className="text-3xl font-bold text-white mb-6 text-center">
                    Register
                </h1>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <motion.div variants={inputVariants}>
                        <div className="space-y-2">
                            <label
                                htmlFor="username"
                                className="text-gray-300 font-medium flex items-center"
                            >
                                <User className="mr-2 w-4 h-4" />
                                Username
                            </label>
                            <input
                                type="text"
                                id="username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="bg-black/20 text-white border-purple-500/30
                                           placeholder:text-gray-500 focus:ring-purple-500
                                           focus:border-purple-500/50 transition-colors duration-300
                                           shadow-sm shadow-purple-500/20 w-full rounded-md py-2.5 px-3.5"
                                placeholder="Enter your username"
                            />
                        </div>
                    </motion.div>
                    <motion.div variants={inputVariants}>
                        <div className="space-y-2">
                            <label
                                htmlFor="email"
                                className="text-gray-300 font-medium flex items-center"
                            >
                                <Mail className="mr-2 w-4 h-4" />
                                Email
                            </label>
                            <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="bg-black/20 text-white border-purple-500/30
                                           placeholder:text-gray-500 focus:ring-purple-500
                                           focus:border-purple-500/50 transition-colors duration-300
                                           shadow-sm shadow-purple-500/20 w-full rounded-md py-2.5 px-3.5"
                                placeholder="Enter your email"
                            />
                        </div>
                    </motion.div>
                    <motion.div variants={inputVariants}>
                        <div className="space-y-2">
                            <label
                                htmlFor="password"
                                className="text-gray-300 font-medium flex items-center"
                            >
                                <Lock className="mr-2 w-4 h-4" />
                                Password
                            </label>
                            <input
                                type="password"
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-black/20 text-white border-purple-500/30
                                           placeholder:text-gray-500 focus:ring-purple-500
                                           focus:border-purple-500/50 transition-colors duration-300
                                           shadow-sm shadow-purple-500/20 w-full rounded-md py-2.5 px-3.5"
                                placeholder="Enter your password"
                            />
                        </div>
                    </motion.div>
                    <motion.div variants={inputVariants}>
                        <div className="space-y-2">
                            <label
                                htmlFor="confirmPassword"
                                className="text-gray-300 font-medium flex items-center"
                            >
                                <Lock className="mr-2 w-4 h-4" />
                                Confirm Password
                            </label>
                            <input
                                type="password"
                                id="confirmPassword"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="bg-black/20 text-white border-purple-500/30
                                           placeholder:text-gray-500 focus:ring-purple-500
                                           focus:border-purple-500/50 transition-colors duration-300
                                           shadow-sm shadow-purple-500/20 w-full rounded-md py-2.5 px-3.5"
                                placeholder="Confirm your password"
                            />
                        </div>
                    </motion.div>
                    {error && (
                        <p className="text-red-400 text-sm mt-2 bg-red-500/10 p-2 rounded-md border border-red-500/20">
                            {error}
                        </p>
                    )}
                    <motion.div
                        variants={buttonVariants}
                        whileHover="hover"
                        whileTap="tap"
                    >
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-green-500 to-blue-500
                                       text-white font-semibold py-3 rounded-full
                                       shadow-lg hover:shadow-xl transition-all duration-300
                                       hover:scale-105
                                       loading:opacity-70 loading:cursor-not-allowed"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Registering...
                                </>
                            ) : (
                                "Register"
                            )}
                        </button>
                    </motion.div>
                    <div className="text-center text-gray-400 text-sm mt-4">
                        <a
                            href="/login" // Adjust the URL as needed
                            className="hover:text-purple-300 transition-colors"
                        >
                            Already have an account? Log In
                        </a>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default RegistrationForm;
