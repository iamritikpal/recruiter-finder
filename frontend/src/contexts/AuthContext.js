import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already authenticated on app load
  useEffect(() => {
    const authStatus = localStorage.getItem("isAuthenticated");
    if (authStatus === "true") {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = (email, password) => {
    // Get credentials from environment variables
    const validEmail = process.env.REACT_APP_LOGIN_EMAIL;
    const validPassword = process.env.REACT_APP_LOGIN_PASSWORD;

    if (email === validEmail && password === validPassword) {
      setIsAuthenticated(true);
      localStorage.setItem("isAuthenticated", "true");
      return { success: true };
    } else {
      return {
        success: false,
        error:
          "Invalid credentials. Please request access if you need early access to this platform.",
      };
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem("isAuthenticated");
  };

  const value = {
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
