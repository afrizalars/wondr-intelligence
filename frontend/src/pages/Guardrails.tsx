import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Guardrails: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Guardrails
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Content filtering and guardrails management coming soon...</Typography>
      </Paper>
    </Box>
  );
};

export default Guardrails;