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
  LinearProgress,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Badge,
  CheckCircle,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import BrandLogo from '../components/BrandLogo';

const RegisterApple: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const { register } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name || undefined,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Password strength calculator
  const getPasswordStrength = () => {
    const pass = formData.password;
    if (!pass) return 0;
    let strength = 0;
    if (pass.length >= 8) strength += 25;
    if (pass.length >= 12) strength += 25;
    if (/[a-z]/.test(pass) && /[A-Z]/.test(pass)) strength += 25;
    if (/\d/.test(pass) && /[^a-zA-Z\d]/.test(pass)) strength += 25;
    return strength;
  };

  const passwordStrength = getPasswordStrength();
  const getStrengthColor = () => {
    if (passwordStrength <= 25) return '#FF3B30';
    if (passwordStrength <= 50) return '#FF9500';
    if (passwordStrength <= 75) return '#FFCC00';
    return '#34C759';
  };

  const getFieldSx = (fieldName: string) => ({
    '& .MuiOutlinedInput-root': {
      height: '56px',
      borderRadius: '16px',
      backgroundColor: '#F7F7F9',
      border: 'none',
      transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      '& fieldset': {
        border: focusedField === fieldName ? '2px solid #007AFF' : '1px solid transparent',
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
  });

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
            maxWidth: 480,
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
              pt: 5,
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
              Create Account
            </Typography>
            <Typography
              sx={{
                fontSize: '18px',
                color: '#86868b',
                fontWeight: 400,
              }}
            >
              Join Wondr Intelligence today
            </Typography>
          </Box>

          {/* Form */}
          <Box sx={{ p: 5, pt: 4 }}>
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
              <Stack spacing={2.5}>
                <TextField
                  fullWidth
                  placeholder="Email address"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
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
                  sx={getFieldSx('email')}
                />

                <TextField
                  fullWidth
                  placeholder="Username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  autoComplete="username"
                  onFocus={() => setFocusedField('username')}
                  onBlur={() => setFocusedField(null)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={{ color: focusedField === 'username' ? '#007AFF' : '#8E8E93' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={getFieldSx('username')}
                />

                <TextField
                  fullWidth
                  placeholder="Full name (optional)"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  autoComplete="name"
                  onFocus={() => setFocusedField('full_name')}
                  onBlur={() => setFocusedField(null)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Badge sx={{ color: focusedField === 'full_name' ? '#007AFF' : '#8E8E93' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={getFieldSx('full_name')}
                />

                <Box>
                  <TextField
                    fullWidth
                    placeholder="Password"
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    autoComplete="new-password"
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
                    sx={getFieldSx('password')}
                  />
                  {formData.password && (
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={passwordStrength}
                        sx={{
                          height: 4,
                          borderRadius: 2,
                          backgroundColor: '#E5E5EA',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getStrengthColor(),
                            borderRadius: 2,
                          },
                        }}
                      />
                      <Typography
                        sx={{
                          fontSize: '12px',
                          color: getStrengthColor(),
                          mt: 0.5,
                          fontWeight: 500,
                        }}
                      >
                        {passwordStrength <= 25 && 'Weak password'}
                        {passwordStrength > 25 && passwordStrength <= 50 && 'Fair password'}
                        {passwordStrength > 50 && passwordStrength <= 75 && 'Good password'}
                        {passwordStrength > 75 && 'Strong password'}
                      </Typography>
                    </Box>
                  )}
                </Box>

                <TextField
                  fullWidth
                  placeholder="Confirm password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  autoComplete="new-password"
                  onFocus={() => setFocusedField('confirmPassword')}
                  onBlur={() => setFocusedField(null)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: focusedField === 'confirmPassword' ? '#007AFF' : '#8E8E93' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        {formData.confirmPassword && formData.password === formData.confirmPassword ? (
                          <CheckCircle sx={{ color: '#34C759' }} />
                        ) : (
                          <IconButton
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            edge="end"
                            sx={{
                              color: '#8E8E93',
                              '&:hover': { color: '#007AFF' },
                            }}
                          >
                            {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        )}
                      </InputAdornment>
                    ),
                  }}
                  sx={getFieldSx('confirmPassword')}
                />

                <Button
                  type="submit"
                  fullWidth
                  disabled={loading || !formData.email || !formData.username || !formData.password}
                  sx={{
                    height: '52px',
                    borderRadius: '26px',
                    background: loading || !formData.email || !formData.username || !formData.password
                      ? '#E5E5EA'
                      : 'linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%)',
                    color: loading || !formData.email || !formData.username || !formData.password
                      ? '#8E8E93'
                      : '#FFFFFF',
                    fontSize: '17px',
                    fontWeight: 600,
                    letterSpacing: '-0.01em',
                    textTransform: 'none',
                    border: 'none',
                    boxShadow: loading || !formData.email || !formData.username || !formData.password
                      ? 'none'
                      : '0 4px 12px rgba(0, 122, 255, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                    mt: 2,
                    '&:hover': {
                      background: loading || !formData.email || !formData.username || !formData.password
                        ? '#E5E5EA'
                        : 'linear-gradient(135deg, #0051D5 0%, #007AFF 100%)',
                      boxShadow: loading || !formData.email || !formData.username || !formData.password
                        ? 'none'
                        : '0 8px 20px rgba(0, 122, 255, 0.4)',
                      transform: loading || !formData.email || !formData.username || !formData.password
                        ? 'none'
                        : 'translateY(-1px)',
                    },
                    '&:active': {
                      transform: 'translateY(0)',
                    },
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} sx={{ color: '#8E8E93' }} />
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </Stack>
            </form>

            {/* Footer Link */}
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Typography
                sx={{
                  fontSize: '14px',
                  color: '#8E8E93',
                }}
              >
                Already have an account?{' '}
                <Link
                  to="/auth/login"
                  style={{
                    color: '#007AFF',
                    textDecoration: 'none',
                    fontWeight: 600,
                    transition: 'color 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#0051D5')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#007AFF')}
                >
                  Sign In
                </Link>
              </Typography>
            </Box>
          </Box>
        </Box>
      </Fade>
    </Box>
  );
};

export default RegisterApple;