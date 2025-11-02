import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user] = useState({
    user_id: 'demo_user',
    username: 'sridhar_demo',
    email: 'sridhar@guidora.com',
    full_name: 'Sridhar Shanmugam'
  });
  const [isAuthenticated] = useState(true);
  const [loading] = useState(false);

  const value = {
    user,
    loading,
    isAuthenticated,
    login: () => console.log('Login'),
    register: () => console.log('Register'),
    logout: () => console.log('Logout')
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
