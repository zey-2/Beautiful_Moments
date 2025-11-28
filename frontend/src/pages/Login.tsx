import React, { useState } from "react";
import { verifyPassword } from "../api";
import "./Login.css";

interface LoginProps {
    onLogin: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const result = await verifyPassword(password);
            if (result.success) {
                localStorage.setItem("authenticated", "true");
                onLogin();
            } else {
                setError(result.message || "Incorrect password");
            }
        } catch (err) {
            setError("Failed to verify password. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h1 className="login-title">Enter Edit Mode</h1>
                <p className="login-subtitle">Please enter the password to continue</p>

                <form onSubmit={handleSubmit} className="login-form">
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        className="login-input"
                        disabled={loading}
                        autoFocus
                    />

                    {error && <div className="login-error">{error}</div>}

                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading || !password}
                    >
                        {loading ? "Verifying..." : "Enter"}
                    </button>
                </form>
            </div>
        </div>
    );
};
