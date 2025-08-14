import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const AuthLayout: React.FC = () => {
  const { user } = useAuth();

  if (user) {
    return <Navigate to="/playground" replace />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Outlet />
      </Container>
    </Box>
  );
};

export default AuthLayout;