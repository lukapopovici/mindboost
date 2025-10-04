import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CssBaseline } from '@mui/material';
import './App.css';
import './styles/theme.css';

// O componentă care protejează rutele
const PrivateRoute = ({ children }: { children: JSX.Element }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
                path="/"
                element={
                    <PrivateRoute>
                        <DashboardPage />
                    </PrivateRoute>
                }
            />
            {/* Adaugă aici alte rute, ex: /register */}
        </Routes>
    );
};

function App() {
    return (
        <AuthProvider>
            <CssBaseline />
            <AppRoutes />
        </AuthProvider>
    );
}

export default App;