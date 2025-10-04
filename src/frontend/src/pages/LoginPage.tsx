import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Box, Button, Container, TextField, Typography, Alert, Paper, Chip } from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import LoginIcon from '@mui/icons-material/Login';
import '../App.css';

export const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleLogin = async (event: React.FormEvent) => {
        event.preventDefault();
        setError('');
        try {
            await login(email, password);
            navigate('/'); // Redirecționează către dashboard după login reușit
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        }
    };

    return (
        <div className="login-page-background">
            <Box sx={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 2,
                minHeight: '100vh'
            }}>
                <Container component="main" maxWidth="sm">
                <Paper 
                    elevation={0}
                    className="feature-card"
                    sx={{ 
                        padding: 4,
                        borderRadius: 4,
                        position: 'relative',
                        zIndex: 1
                    }}
                >
                    <Box sx={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        alignItems: 'center',
                        textAlign: 'center'
                    }}>
                        {/* Logo and Title */}
                        <Box sx={{ 
                            background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                            borderRadius: '50%',
                            padding: 2,
                            marginBottom: 3
                        }}>
                            <PsychologyIcon sx={{ fontSize: '3rem', color: 'white' }} />
                        </Box>
                        
                        <Typography 
                            component="h1" 
                            variant="h3"
                            sx={{
                                fontFamily: 'Crimson Text, serif',
                                fontWeight: 600,
                                color: '#ffffff',
                                marginBottom: 1
                            }}
                        >
                            MindBoost AI
                        </Typography>
                        
                        <Typography 
                            variant="body1" 
                            sx={{ 
                                color: '#f1f5f9', 
                                marginBottom: 3,
                                maxWidth: 400
                            }}
                        >
                            Welcome to your intelligent academic companion. Sign in to unlock personalized learning experiences.
                        </Typography>
                        
                        <Chip 
                            label="Academic Excellence Platform" 
                            sx={{ 
                                background: 'rgba(255,255,255,0.15)',
                                color: '#ffffff',
                                marginBottom: 4,
                                fontWeight: 500,
                                backdropFilter: 'blur(10px)'
                            }} 
                        />

                        <Box 
                            component="form" 
                            onSubmit={handleLogin} 
                            noValidate 
                            sx={{ width: '100%', maxWidth: 400 }}
                        >
                            <TextField 
                                margin="normal" 
                                required 
                                fullWidth 
                                id="email" 
                                label="Email Address" 
                                name="email" 
                                autoComplete="email" 
                                autoFocus 
                                value={email} 
                                onChange={(e) => setEmail(e.target.value)}
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        borderRadius: 2,
                                        '&.Mui-focused fieldset': {
                                            borderColor: '#3b82f6',
                                        },
                                    },
                                    '& .MuiInputLabel-root.Mui-focused': {
                                        color: '#3b82f6',
                                    },
                                }}
                            />
                            <TextField 
                                margin="normal" 
                                required 
                                fullWidth 
                                name="password" 
                                label="Password" 
                                type="password" 
                                id="password" 
                                autoComplete="current-password" 
                                value={password} 
                                onChange={(e) => setPassword(e.target.value)}
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        borderRadius: 2,
                                        '&.Mui-focused fieldset': {
                                            borderColor: '#3b82f6',
                                        },
                                    },
                                    '& .MuiInputLabel-root.Mui-focused': {
                                        color: '#3b82f6',
                                    },
                                }}
                            />
                            
                            {error && (
                                <Alert 
                                    severity="error" 
                                    sx={{ 
                                        mt: 2, 
                                        width: '100%',
                                        borderRadius: 2
                                    }}
                                >
                                    {error}
                                </Alert>
                            )}
                            
                            <Button 
                                type="submit" 
                                fullWidth 
                                variant="contained" 
                                startIcon={<LoginIcon />}
                                sx={{ 
                                    mt: 3, 
                                    mb: 2,
                                    py: 1.5,
                                    borderRadius: 2,
                                    fontSize: '1.1rem',
                                    fontWeight: 600,
                                    textTransform: 'none',
                                    background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                                    boxShadow: '0 8px 25px rgba(30, 58, 138, 0.15)',
                                    '&:hover': {
                                        background: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
                                        transform: 'translateY(-2px)',
                                        boxShadow: '0 12px 40px rgba(30, 58, 138, 0.2)',
                                    },
                                }}
                            >
                                Sign In to MindBoost
                            </Button>
                            
                            <Typography 
                                variant="body2" 
                                sx={{ 
                                    color: '#e2e8f0', 
                                    textAlign: 'center',
                                    mt: 2
                                }}
                            >
                                Don't have an account? Contact your administrator.
                            </Typography>
                        </Box>
                    </Box>
                </Paper>
            </Container>
            </Box>
        </div>
    );
};