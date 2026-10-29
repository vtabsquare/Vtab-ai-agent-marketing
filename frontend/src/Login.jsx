import React, { useState } from 'react';
import { Bot, Icon } from './Bots.jsx';
import { api } from './api.js';

export function Login({ onLogin }) {
  const [email, setEmail] = useState('vitabsquare@gmail.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Please enter both email and password.');
      return;
    }
    setError('');
    setBusy(true);
    try {
      const res = await api('/auth/login', 'POST', {
        email: email.trim().toLowerCase(),
        password: password
      });
      if (res && res.user) {
        onLogin(res.user);
      } else {
        setError('Authentication failed. Please check your credentials.');
      }
    } catch (err) {
      setError(err.message || 'The email or password is incorrect.');
    } finally {
      setBusy(false);
    }
  }

  async function handleLaunchDemo() {
    setError('');
    setBusy(true);
    try {
      const res = await api('/auth/demo', 'POST');
      if (res && res.user) {
        onLogin(res.user);
      } else {
        setError('Failed to initialize pilot demo session.');
      }
    } catch (err) {
      setError(err.message || 'Could not connect to pilot demo session.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-header">
          <div className="login-badge">
            <Bot role="manager" size={56} />
          </div>
          <h1>Marketing OS</h1>
          <p className="login-subtitle">Sign in to your autonomous marketing workspace</p>
        </div>

        {error && (
          <div className="notice error login-error" role="alert">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <label>
            Email address
            <input
              type="email"
              required
              autoFocus
              autoComplete="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="name@company.com"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter workspace password"
            />
          </label>

          <button type="submit" className="button primary full login-btn" disabled={busy}>
            {busy ? 'Authenticating…' : 'Sign in to workspace'}
            <Icon name="arrow" size={14} />
          </button>
        </form>

        <div className="login-divider">
          <span>OR</span>
        </div>

        <button
          type="button"
          className="button secondary full pilot-launch-btn"
          onClick={handleLaunchDemo}
          disabled={busy}
        >
          <span>🚀 Explore Interactive Pilot Demo</span>
          <Icon name="arrow" size={14} />
        </button>

        <div className="login-footer">
          <span className="status-dot" />
          <span>Secure AES-256 session · Private multi-agent workspace</span>
        </div>
      </div>
    </div>
  );
}
