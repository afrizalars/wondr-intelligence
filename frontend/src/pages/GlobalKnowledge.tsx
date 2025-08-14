import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const GlobalKnowledge: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Global Knowledge
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Document upload and knowledge management coming soon...</Typography>
      </Paper>
    </Box>
  );
};

export default GlobalKnowledge;