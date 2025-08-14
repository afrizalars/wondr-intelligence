import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const SearchHistory: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Search History
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Search history viewer coming soon...</Typography>
      </Paper>
    </Box>
  );
};

export default SearchHistory;