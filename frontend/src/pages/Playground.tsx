import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Divider,
  Chip,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Avatar,
  Fade,
  Grow,
  LinearProgress,
  Stack,
  InputAdornment,
  Container,
  Grid,
  useTheme,
  alpha,
  Skeleton,
} from '@mui/material';
import {
  Send as SendIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Store as StoreIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingIcon,
  Search as SearchIcon,
  AutoAwesome as AutoAwesomeIcon,
  QueryStats as QueryStatsIcon,
  Speed as SpeedIcon,
  Source as SourceIcon,
  Psychology as PsychologyIcon,
  Smartphone as SmartphoneIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { searchApi } from '../api/search';

interface SearchResult {
  query: string;
  cif: string;
  answer: string;
  citations: Array<{
    source: string;
    title: string;
    text_snippet: string;
    similarity_score: number;
  }>;
  latency_ms: number;
  model_used: string;
}

const MobilePreview: React.FC<{ result?: SearchResult | null }> = ({ result }) => {
  const theme = useTheme();
  
  return (
    <Paper
      elevation={10}
      sx={{
        width: 375,
        height: 812,
        bgcolor: '#1a1a1a',
        borderRadius: 6,
        p: 1.5,
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%)',
      }}
    >
      <Box
        sx={{
          width: '100%',
          height: '100%',
          bgcolor: '#fff',
          borderRadius: 5,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 'inset 0 0 0 1px rgba(0,0,0,0.1)',
        }}
      >
        {/* Phone Status Bar */}
        <Box
          sx={{
            height: 44,
            bgcolor: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 2.5,
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="caption" sx={{ fontWeight: 600 }}>9:41</Typography>
          <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
            <Box sx={{ width: 4, height: 4, bgcolor: 'text.primary', borderRadius: '50%' }} />
            <Box sx={{ width: 4, height: 4, bgcolor: 'text.primary', borderRadius: '50%' }} />
            <Box sx={{ width: 4, height: 4, bgcolor: 'text.primary', borderRadius: '50%' }} />
            <Typography variant="caption">📶</Typography>
            <Typography variant="caption">🔋</Typography>
          </Box>
        </Box>

        {/* App Header */}
        <Box
          sx={{
            p: 2.5,
            background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
            color: 'white',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: -0.5 }}>
            Wondr Banking
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.9 }}>
            AI-Powered Insights
          </Typography>
        </Box>

        {/* Search Bar */}
        <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Ask about your transactions..."
            value={result?.query || ''}
            InputProps={{
              sx: { 
                borderRadius: 3,
                bgcolor: 'white',
                '& fieldset': { border: '1px solid', borderColor: 'divider' }
              },
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Content Area */}
        <Box sx={{ flex: 1, overflowY: 'auto', bgcolor: 'grey.50', p: 2 }}>
          {result ? (
            <Fade in={true}>
              <Box>
                {/* AI Response Card */}
                <Card 
                  sx={{ 
                    mb: 2, 
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    boxShadow: '0 10px 40px rgba(102, 126, 234, 0.3)',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                      <Avatar sx={{ 
                        width: 32, 
                        height: 32, 
                        mr: 1.5, 
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        backdropFilter: 'blur(10px)',
                      }}>
                        <AutoAwesomeIcon sx={{ fontSize: 18 }} />
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          AI Assistant
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.9 }}>
                          Personalized insights
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.6 }}>
                      {result.answer}
                    </Typography>
                    <Chip
                      label={`Based on ${result.citations.length} transactions`}
                      size="small"
                      sx={{ 
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        color: 'white',
                        backdropFilter: 'blur(10px)',
                      }}
                    />
                  </CardContent>
                </Card>

                {/* Transaction List */}
                <Typography variant="subtitle2" sx={{ mb: 1.5, color: 'text.secondary' }}>
                  Related Transactions
                </Typography>
                {result.citations.slice(0, 3).map((citation, index) => (
                  <Grow in={true} key={index} timeout={300 + index * 100}>
                    <Card sx={{ 
                      mb: 1.5, 
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      bgcolor: 'white',
                    }}>
                      <CardContent sx={{ py: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ 
                            width: 40, 
                            height: 40, 
                            mr: 2,
                            bgcolor: alpha(theme.palette.primary.main, 0.1),
                            color: 'primary.main',
                          }}>
                            <StoreIcon sx={{ fontSize: 20 }} />
                          </Avatar>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {citation.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {citation.text_snippet.substring(0, 60)}...
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grow>
                ))}
              </Box>
            </Fade>
          ) : (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <QueryStatsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Ask questions about your spending
              </Typography>
              <Typography variant="caption" color="text.disabled">
                Try "What did I spend on groceries?"
              </Typography>
            </Box>
          )}
        </Box>

        {/* Bottom Navigation */}
        <Box
          sx={{
            height: 65,
            borderTop: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-around',
            bgcolor: '#fff',
            boxShadow: '0 -2px 10px rgba(0,0,0,0.05)',
          }}
        >
          {['🏠', '💳', '📊', '👤'].map((icon, index) => (
            <IconButton 
              key={index}
              size="small"
              sx={{ 
                fontSize: 24,
                color: index === 2 ? 'primary.main' : 'text.secondary',
              }}
            >
              {icon}
            </IconButton>
          ))}
        </Box>
      </Box>
    </Paper>
  );
};

const Playground: React.FC = () => {
  const theme = useTheme();
  const [query, setQuery] = useState('');
  const [cif, setCif] = useState('CIF00000001');
  const [showCitations, setShowCitations] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);

  const searchMutation = useMutation({
    mutationFn: searchApi.magicSearch,
    onSuccess: (data) => {
      setResult(data);
      setShowCitations(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate({
        query,
        cif,
        include_global: true,
        top_k: 10,
        similarity_threshold: 0.5,
        use_guardrails: true,
      });
    }
  };

  const exampleQueries = [
    "What did I spend on restaurants last month?",
    "Show me my largest transactions",
    "How much did I save this quarter?",
    "Analyze my shopping patterns"
  ];

  return (
    <Box sx={{ 
      minHeight: 'calc(100vh - 64px)', 
      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.02)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
    }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, letterSpacing: -0.5 }}>
            <AutoAwesomeIcon sx={{ mr: 1.5, fontSize: 32, verticalAlign: 'middle', color: 'primary.main' }} />
            Magic Search Playground
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Experience AI-powered transaction insights with natural language queries
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* Left Panel - Search Interface */}
          <Grid item xs={12} lg={7}>
            <Stack spacing={3}>
              {/* Search Card */}
              <Paper 
                elevation={0}
                sx={{ 
                  p: 4, 
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: 'divider',
                  background: 'white',
                }}
              >
                <form onSubmit={handleSubmit}>
                  <Stack spacing={3}>
                    {/* Customer Selection */}
                    <FormControl fullWidth>
                      <InputLabel>Select Customer</InputLabel>
                      <Select
                        value={cif}
                        onChange={(e) => setCif(e.target.value)}
                        label="Select Customer"
                        sx={{ borderRadius: 2 }}
                      >
                        {[...Array(20)].map((_, i) => (
                          <MenuItem key={i} value={`CIF${String(i + 1).padStart(8, '0')}`}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Avatar sx={{ width: 24, height: 24, mr: 1.5, fontSize: 12 }}>
                                {i + 1}
                              </Avatar>
                              Customer {i + 1} - CIF{String(i + 1).padStart(8, '0')}
                            </Box>
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    {/* Query Input */}
                    <Box>
                      <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
                        Your Question
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask anything about transactions, spending patterns, or financial insights..."
                        variant="outlined"
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontSize: '1rem',
                          }
                        }}
                      />
                    </Box>

                    {/* Example Queries */}
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                        Try an example:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {exampleQueries.map((example, index) => (
                          <Chip
                            key={index}
                            label={example}
                            variant="outlined"
                            size="small"
                            onClick={() => setQuery(example)}
                            sx={{ 
                              cursor: 'pointer',
                              '&:hover': { 
                                bgcolor: alpha(theme.palette.primary.main, 0.08),
                                borderColor: 'primary.main',
                              }
                            }}
                          />
                        ))}
                      </Box>
                    </Box>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      fullWidth
                      startIcon={searchMutation.isPending ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                      disabled={searchMutation.isPending || !query.trim()}
                      sx={{
                        py: 1.5,
                        borderRadius: 2,
                        textTransform: 'none',
                        fontSize: '1rem',
                        fontWeight: 600,
                        background: searchMutation.isPending 
                          ? undefined 
                          : `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                      }}
                    >
                      {searchMutation.isPending ? 'Searching...' : 'Search with AI'}
                    </Button>
                  </Stack>
                </form>
              </Paper>

              {/* Loading State */}
              {searchMutation.isPending && (
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 4, 
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <Stack spacing={2}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <CircularProgress size={24} />
                      <Typography>Analyzing your query...</Typography>
                    </Box>
                    <LinearProgress variant="indeterminate" />
                  </Stack>
                </Paper>
              )}

              {/* Error State */}
              {searchMutation.isError && (
                <Alert 
                  severity="error" 
                  sx={{ borderRadius: 2 }}
                  icon={<InfoIcon />}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Search failed
                  </Typography>
                  <Typography variant="body2">
                    Please try again or contact support if the issue persists.
                  </Typography>
                </Alert>
              )}

              {/* Results Section */}
              {result && !searchMutation.isPending && (
                <Fade in={true}>
                  <Paper 
                    elevation={0}
                    sx={{ 
                      borderRadius: 3,
                      border: '1px solid',
                      borderColor: 'divider',
                      overflow: 'hidden',
                    }}
                  >
                    {/* Results Header */}
                    <Box sx={{ 
                      p: 3, 
                      bgcolor: alpha(theme.palette.primary.main, 0.04),
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CheckCircleIcon color="success" />
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            AI Response
                          </Typography>
                        </Box>
                        <Stack direction="row" spacing={1}>
                          <Chip 
                            icon={<SpeedIcon />}
                            label={`${result.latency_ms}ms`} 
                            size="small"
                            variant="outlined"
                          />
                          <Chip 
                            icon={<PsychologyIcon />}
                            label={result.model_used} 
                            size="small"
                            variant="outlined"
                          />
                          <Chip 
                            icon={<SourceIcon />}
                            label={`${result.citations.length} sources`} 
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </Stack>
                      </Box>
                    </Box>

                    {/* Answer Content */}
                    <Box sx={{ p: 3 }}>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          lineHeight: 1.8,
                          color: 'text.primary',
                          mb: 3,
                        }}
                      >
                        {result.answer}
                      </Typography>

                      <Divider sx={{ my: 3 }} />

                      {/* Citations Section */}
                      <Box>
                        <Button
                          onClick={() => setShowCitations(!showCitations)}
                          endIcon={showCitations ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          sx={{ 
                            mb: 2,
                            textTransform: 'none',
                            fontWeight: 600,
                          }}
                        >
                          View Source Documents ({result.citations.length})
                        </Button>
                        
                        <Collapse in={showCitations}>
                          <Stack spacing={2}>
                            {result.citations.map((citation, index) => (
                              <Paper
                                key={index}
                                elevation={0}
                                sx={{ 
                                  p: 2.5,
                                  bgcolor: alpha(theme.palette.primary.main, 0.02),
                                  border: '1px solid',
                                  borderColor: alpha(theme.palette.primary.main, 0.1),
                                  borderRadius: 2,
                                }}
                              >
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                                  <Avatar sx={{ 
                                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                                    color: 'primary.main',
                                    width: 36,
                                    height: 36,
                                  }}>
                                    {index + 1}
                                  </Avatar>
                                  <Box sx={{ flex: 1 }}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                                      {citation.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                                      {citation.text_snippet}
                                    </Typography>
                                    <Stack direction="row" spacing={1}>
                                      <Chip
                                        label={citation.source === 'cif' ? 'Transaction Data' : 'Knowledge Base'}
                                        size="small"
                                        variant="outlined"
                                        color={citation.source === 'cif' ? 'primary' : 'default'}
                                      />
                                      <Chip
                                        label={`${(citation.similarity_score * 100).toFixed(0)}% relevant`}
                                        size="small"
                                        color="success"
                                        variant="outlined"
                                      />
                                    </Stack>
                                  </Box>
                                </Box>
                              </Paper>
                            ))}
                          </Stack>
                        </Collapse>
                      </Box>
                    </Box>
                  </Paper>
                </Fade>
              )}
            </Stack>
          </Grid>

          {/* Right Panel - Mobile Preview */}
          <Grid item xs={12} lg={5}>
            <Box sx={{ 
              position: 'sticky',
              top: 80,
            }}>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
              }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  gap: 1,
                  mb: 1,
                }}>
                  <SmartphoneIcon color="action" />
                  <Typography variant="subtitle2" color="text.secondary">
                    Live Mobile Preview
                  </Typography>
                </Box>
                <MobilePreview result={result} />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Playground;