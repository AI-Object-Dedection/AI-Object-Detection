import React, { useState } from 'react';
import './LoginPage.css';

// Google Icon SVG Component
const GoogleIcon = () => (
  <svg className="google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path
      fill="#4285F4"
      d="M23.745 12.27c0-.79-.07-1.54-.19-2.27h-11.3v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82z"
    />
    <path
      fill="#34A853"
      d="M12.255 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96h-3.98v3.09C3.515 21.3 7.565 24 12.255 24z"
    />
    <path
      fill="#FBBC05"
      d="M5.525 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62h-3.98a11.86 11.86 0 000 10.76l3.98-3.09z"
    />
    <path
      fill="#EA4335"
      d="M12.255 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C18.205 1.19 15.495 0 12.255 0c-4.69 0-8.74 2.7-10.71 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96z"
    />
  </svg>
);

// App Logo Icon
const AppLogoIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="2" />
  </svg>
);

// Lock Icon for Security Badge
const LockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="2" />
    <path
      d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    
    // TODO: This function will be updated during Google OAuth integration
    console.log('Initiating Google Sign-In...');
    
    // Simulated loading (will be removed in real integration)
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon">
            <AppLogoIcon />
          </div>
          <h1 className="login-title">AI Object Detection</h1>
          <p className="login-subtitle">
            Detect and analyze objects in your images with the power of artificial intelligence
          </p>
        </div>

        {/* Welcome Text */}
        <div className="login-welcome">
          <h2>Welcome back</h2>
          <p>Sign in to continue to your dashboard</p>
        </div>

        {/* Google Sign-In Button */}
        <button
          className={`google-signin-btn ${isLoading ? 'loading' : ''}`}
          onClick={handleGoogleSignIn}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="loading-spinner-small"></div>
              <span className="btn-text">Signing in...</span>
            </>
          ) : (
            <>
              <GoogleIcon />
              <span className="btn-text">Sign in with Google</span>
            </>
          )}
        </button>

        {/* Security Badge */}
        <div className="security-badge">
          <LockIcon />
          <span>Secured with Google OAuth 2.0</span>
        </div>

        {/* Footer */}
        <div className="login-footer">
          <p>
            By signing in, you agree to our{' '}
            <a href="/terms" target="_blank" rel="noopener noreferrer">
              Terms of Service
            </a>
            {' '}and{' '}
            <a href="/privacy" target="_blank" rel="noopener noreferrer">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
