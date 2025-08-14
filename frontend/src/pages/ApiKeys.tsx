import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const ApiKeys: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        API Keys
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>API key management coming soon...</Typography>
      </Paper>
    </Box>
  );
};

export default ApiKeys;