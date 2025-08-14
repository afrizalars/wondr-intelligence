import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Merchants: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Merchants Catalog
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Merchant management interface coming soon...</Typography>
      </Paper>
    </Box>
  );
};

export default Merchants;