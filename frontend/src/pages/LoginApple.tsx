import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  alpha,
  Stack,
  InputAdornment,
  IconButton,
  Fade,
  Grow,
} from '@mui/material';
import { Visibility, VisibilityOff, Email, Lock } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import BrandLogo from '../components/BrandLogo';

const LoginApple: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        backgroundSize: '400% 400%',
        animation: 'gradientShift 15s ease infinite',
        '@keyframes gradientShift': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        p: 2,
      }}
    >
      <Fade in timeout={800}>
        <Box
          sx={{
            width: '100%',
            maxWidth: 440,
            background: alpha('#FFFFFF', 0.95),
            backdropFilter: 'blur(20px)',
            borderRadius: '24px',
            boxShadow: '0 24px 48px rgba(0, 0, 0, 0.12)',
            overflow: 'hidden',
            border: `1px solid ${alpha('#FFFFFF', 0.3)}`,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              pt: 6,
              pb: 2,
              px: 5,
              textAlign: 'center',
              borderBottom: `1px solid ${alpha('#000', 0.06)}`,
            }}
          >
            <Grow in timeout={1000}>
              <Box sx={{ mb: 3 }}>
                <BrandLogo />
              </Box>
            </Grow>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                fontSize: '32px',
                color: '#1d1d1f',
                letterSpacing: '-0.025em',
                mb: 1,
              }}
            >
              Welcome Back
            </Typography>
            <Typography
              sx={{
                fontSize: '18px',
                color: '#86868b',
                fontWeight: 400,
              }}
            >
              Sign in to Wondr Intelligence
            </Typography>
          </Box>

          {/* Form */}
          <Box sx={{ p: 5 }}>
            {error && (
              <Grow in>
                <Alert
                  severity="error"
                  sx={{
                    mb: 3,
                    borderRadius: '12px',
                    backgroundColor: alpha('#FF3B30', 0.1),
                    color: '#FF3B30',
                    border: 'none',
                    '& .MuiAlert-icon': {
                      color: '#FF3B30',
                    },
                  }}
                >
                  {error}
                </Alert>
              </Grow>
            )}

            <form onSubmit={handleSubmit}>
              <Stack spacing={3}>
                <TextField
                  fullWidth
                  placeholder="Email address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  autoFocus
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email sx={{ color: focusedField === 'email' ? '#007AFF' : '#8E8E93' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      height: '56px',
                      borderRadius: '16px',
                      backgroundColor: '#F7F7F9',
                      border: 'none',
                      transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                      '& fieldset': {
                        border: focusedField === 'email' ? '2px solid #007AFF' : '1px solid transparent',
                        transition: 'all 0.3s',
                      },
                      '&:hover': {
                        backgroundColor: '#F2F2F7',
                        '& fieldset': {
                          border: '1px solid #D1D1D6',
                        },
                      },
                      '&.Mui-focused': {
                        backgroundColor: '#FFFFFF',
                        boxShadow: `0 0 0 4px ${alpha('#007AFF', 0.1)}`,
                        '& fieldset': {
                          border: '2px solid #007AFF',
                        },
                      },
                    },
                    '& input': {
                      fontSize: '16px',
                      fontWeight: 500,
                      '&::placeholder': {
                        color: '#8E8E93',
                        opacity: 1,
                      },
                    },
                  }}
                />

                <TextField
                  fullWidth
                  placeholder="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: focusedField === 'password' ? '#007AFF' : '#8E8E93' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{
                            color: '#8E8E93',
                            '&:hover': { color: '#007AFF' },
                          }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      height: '56px',
                      borderRadius: '16px',
                      backgroundColor: '#F7F7F9',
                      border: 'none',
                      transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                      '& fieldset': {
                        border: focusedField === 'password' ? '2px solid #007AFF' : '1px solid transparent',
                        transition: 'all 0.3s',
                      },
                      '&:hover': {
                        backgroundColor: '#F2F2F7',
                        '& fieldset': {
                          border: '1px solid #D1D1D6',
                        },
                      },
                      '&.Mui-focused': {
                        backgroundColor: '#FFFFFF',
                        boxShadow: `0 0 0 4px ${alpha('#007AFF', 0.1)}`,
                        '& fieldset': {
                          border: '2px solid #007AFF',
                        },
                      },
                    },
                    '& input': {
                      fontSize: '16px',
                      fontWeight: 500,
                      '&::placeholder': {
                        color: '#8E8E93',
                        opacity: 1,
                      },
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  disabled={loading || !email || !password}
                  sx={{
                    height: '52px',
                    borderRadius: '26px',
                    background: loading || !email || !password 
                      ? '#E5E5EA'
                      : 'linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%)',
                    color: loading || !email || !password ? '#8E8E93' : '#FFFFFF',
                    fontSize: '17px',
                    fontWeight: 600,
                    letterSpacing: '-0.01em',
                    textTransform: 'none',
                    border: 'none',
                    boxShadow: loading || !email || !password 
                      ? 'none'
                      : '0 4px 12px rgba(0, 122, 255, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                    '&:hover': {
                      background: loading || !email || !password 
                        ? '#E5E5EA'
                        : 'linear-gradient(135deg, #0051D5 0%, #007AFF 100%)',
                      boxShadow: loading || !email || !password 
                        ? 'none'
                        : '0 8px 20px rgba(0, 122, 255, 0.4)',
                      transform: loading || !email || !password ? 'none' : 'translateY(-1px)',
                    },
                    '&:active': {
                      transform: 'translateY(0)',
                    },
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} sx={{ color: '#8E8E93' }} />
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </Stack>
            </form>

            {/* Footer Links */}
            <Stack spacing={2} sx={{ mt: 4, textAlign: 'center' }}>
              <Typography
                sx={{
                  fontSize: '14px',
                  color: '#8E8E93',
                }}
              >
                Don't have an account?{' '}
                <Link
                  to="/auth/register"
                  style={{
                    color: '#007AFF',
                    textDecoration: 'none',
                    fontWeight: 600,
                    transition: 'color 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#0051D5')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#007AFF')}
                >
                  Create Account
                </Link>
              </Typography>
              
              <Link
                to="/auth/forgot-password"
                style={{
                  fontSize: '14px',
                  color: '#8E8E93',
                  textDecoration: 'none',
                  transition: 'color 0.2s',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = '#007AFF')}
                onMouseLeave={(e) => (e.currentTarget.style.color = '#8E8E93')}
              >
                Forgot Password?
              </Link>
            </Stack>
          </Box>
        </Box>
      </Fade>
    </Box>
  );
};

export default LoginApple;