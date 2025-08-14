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
  Stack,
  // InputAdornment,
  Container,
  Grid,
  // useTheme,
  alpha,
  Fade,
  // Grow,
  Skeleton,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Search as SearchIcon,
  Timer as TimerIcon,
  DataObject as DataObjectIcon,
  CheckCircle as CheckCircleIcon,
  // ExpandMore as ExpandMoreIcon,
  // ExpandLess as ExpandLessIcon,
  ArrowForward as ArrowForwardIcon,
  Lightbulb as LightbulbIcon,
  Psychology as PsychologyIcon,
  TipsAndUpdates as TipsIcon,
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { searchApi } from '../api/search';
import { appleColors, appleBorderRadius, appleShadows } from '../theme/appleTheme';
import BrandLogo from '../components/BrandLogo';

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
  transactions?: Array<{
    merchant: string;
    amount: number;
    date: string;
    category: string;
    title: string;
    text: string;
  }>;
  latency_ms: number;
  model_used: string;
}

// Glassmorphism component wrapper with forwardRef
const GlassCard = React.forwardRef<HTMLDivElement, { children: React.ReactNode; sx?: any }>(
  ({ children, sx = {} }, ref) => {
    return (
      <Paper
        ref={ref}
        elevation={0}
        sx={{
          background: appleColors.glass.ultraLight,
          backdropFilter: appleColors.blur.medium,
          border: `1px solid ${alpha(appleColors.neutral[200], 0.3)}`,
          borderRadius: `${appleBorderRadius.xl}px`,
          boxShadow: appleShadows.glass,
          transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          ...sx,
        }}
      >
        {children}
      </Paper>
    );
  }
);

GlassCard.displayName = 'GlassCard';

// Apple-style mobile preview with transaction-based UI matching reference
const AppleMobilePreview: React.FC<{ result?: SearchResult | null }> = ({ result }) => {
  // const theme = useTheme();
  const [showDetails, setShowDetails] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<any>(null);
  const [searchValue, setSearchValue] = useState('');
  // const [showMobileCitations, setShowMobileCitations] = useState(false);
  // const [showFullTransactions, setShowFullTransactions] = useState(false);
  
  // Generate merchant logos
  const getMerchantLogo = (name: string) => {
    const logoMap: { [key: string]: { bg: string; text: string; color: string; isIcon?: boolean } } = {
      'Starbucks': { bg: '#00704A', text: '☕', color: 'white', isIcon: true },
      "Dunkin'": { bg: '#FF671F', text: 'DN', color: 'white' },
      'Google': { bg: '#4285F4', text: 'G', color: 'white' },
      'Monthly Savings': { bg: '#1C1C1E', text: 'M', color: 'white' },
      'Crypto.com': { bg: '#002D74', text: '₿', color: 'white', isIcon: true },
    };
    return logoMap[name] || { bg: '#E5E5EA', text: name.charAt(0), color: '#8E8E93' };
  };
  
  // Generate contextual transaction data based on search
  const generateTransactions = () => {
    const baseTransactions = [
      { id: 1, name: "Dunkin'", category: 'Food and drink', amount: -5.92, date: 'Yesterday', dateGroup: 'Yesterday', status: 'Booked' },
      { id: 2, name: 'Starbucks', category: 'Food and drink', amount: -3.71, date: 'Yesterday 01:00', dateGroup: 'Yesterday', status: 'Booked', location: 'STARBUCKS COFFEE BROOKLYN NY' },
      { id: 3, name: "Dunkin'", category: 'Food and drink', amount: -7.48, date: 'Tuesday 29 Apr 2025', dateGroup: 'Tuesday 29 Apr 2025', status: 'Booked' },
      { id: 4, name: 'Google', category: 'Income', amount: 4024.34, date: 'Monday 28 Apr 2025', dateGroup: 'Monday 28 Apr 2025', status: 'Booked' },
      { id: 5, name: 'Monthly Savings', category: 'Pensions savings and investments', amount: -200.00, date: 'Monday 28 Apr 2025', dateGroup: 'Monday 28 Apr 2025', status: 'Booked' },
      { id: 6, name: 'Starbucks', category: 'Food and drink', amount: -3.35, date: 'Monday 28 Apr 2025', dateGroup: 'Monday 28 Apr 2025', status: 'Booked' },
      { id: 7, name: "Dunkin'", category: 'Food and drink', amount: -5.83, date: 'Friday 25 Apr 2025', dateGroup: 'Friday 25 Apr 2025', status: 'Booked' },
      { id: 8, name: 'Crypto.com', category: 'Pensions savings and investments', amount: -58.00, date: 'Friday 25 Apr 2025', dateGroup: 'Friday 25 Apr 2025', status: 'Booked' },
    ];

    if (!result?.query && !searchValue) {
      return baseTransactions;
    }

    const query = (result?.query || searchValue).toLowerCase();
    
    if (query.includes('starbucks')) {
      return baseTransactions.filter(t => t.name === 'Starbucks');
    }
    
    if (query.includes('dunkin')) {
      return baseTransactions.filter(t => t.name === "Dunkin'");
    }
    
    if (query.includes('coffee') || query.includes('food')) {
      return baseTransactions.filter(t => t.category === 'Food and drink');
    }
    
    if (query.includes('savings') || query.includes('investment')) {
      return baseTransactions.filter(t => t.category.includes('savings'));
    }
    
    // Filter by search value
    if (searchValue) {
      return baseTransactions.filter(t => 
        t.name.toLowerCase().includes(searchValue.toLowerCase()) ||
        t.category.toLowerCase().includes(searchValue.toLowerCase())
      );
    }
    
    return baseTransactions;
  };
  
  const transactions = generateTransactions();
  
  // Group transactions by date
  const groupedTransactions = transactions.reduce((groups: any, transaction) => {
    const group = transaction.dateGroup;
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(transaction);
    return groups;
  }, {});
  
  // Generate intelligent insights based on search and data
  const generateIntelligentInsight = () => {
    const query = (result?.query || searchValue || '').toLowerCase();
    
    if (query.includes('starbucks')) {
      const starbucksTotal = transactions
        .filter(t => t.name === 'Starbucks')
        .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      const count = transactions.filter(t => t.name === 'Starbucks').length;
      
      // Use the AI response if available, otherwise use default format
      const summary = result?.answer || 
        `You've spent $${starbucksTotal.toFixed(2)} at Starbucks this month, which is $9 more than last month. Starbucks makes up 12% of your total Food And Drink spending this month.`;
      
      return {
        merchant: 'Starbucks',
        logo: getMerchantLogo('Starbucks'),
        summary: summary,
        viewText: `View ${count} transactions`,
        location: 'STARBUCKS COFFEE BROOKLYN NY',
        amount: transactions.find(t => t.name === 'Starbucks')?.amount || -3.71,
        category: 'Food and drink',
        subcategory: 'Coffee',
        date: 'Yesterday 01:00',
        type: 'Debit',
        status: 'Booked',
        citations: result?.citations
      };
    }
    
    if (query.includes('dunkin')) {
      const dunkinTotal = transactions
        .filter(t => t.name === "Dunkin'")
        .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      const count = transactions.filter(t => t.name === "Dunkin'").length;
      
      // Use the AI response if available, otherwise use default format
      const summary = result?.answer || 
        `You've spent $${dunkinTotal.toFixed(2)} at Dunkin' this month, up $6.50 from last month. Your average visit costs $${(dunkinTotal/count).toFixed(2)}.`;
      
      return {
        merchant: "Dunkin'",
        logo: getMerchantLogo("Dunkin'"),
        summary: summary,
        viewText: `View ${count} transactions`,
        location: "DUNKIN' DONUTS #12345",
        amount: transactions.find(t => t.name === "Dunkin'")?.amount || -5.92,
        category: 'Food and drink',
        subcategory: 'Coffee',
        date: 'Yesterday',
        type: 'Debit',
        status: 'Booked',
        citations: result?.citations
      };
    }
    
    // Default insight - use AI response directly
    if (result) {
      return {
        summary: result.answer,
        viewText: `View ${transactions.length} transactions`,
        citations: result.citations
      };
    }
    
    return null;
  };
  
  return (
    <Box
      sx={{
        width: 390,
        height: 844,
        borderRadius: `${appleBorderRadius.xxl * 2}px`,
        background: 'linear-gradient(145deg, #1C1C1E 0%, #2C2C2E 100%)',
        p: 1.2,
        boxShadow: '0 50px 100px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '50%',
          left: -2,
          width: 3,
          height: 60,
          backgroundColor: '#2C2C2E',
          borderRadius: '0 3px 3px 0',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '30%',
          right: -2,
          width: 3,
          height: 40,
          backgroundColor: '#2C2C2E',
          borderRadius: '3px 0 0 3px',
        },
      }}
    >
      <Box
        sx={{
          width: '100%',
          height: '100%',
          borderRadius: `${appleBorderRadius.xxl * 1.8}px`,
          overflow: 'hidden',
          backgroundColor: '#F2F2F7',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Dynamic Island */}
        <Box
          sx={{
            position: 'absolute',
            top: 10,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 120,
            height: 35,
            backgroundColor: '#000',
            borderRadius: appleBorderRadius.pill,
            zIndex: 10,
          }}
        />
        
        {/* Status Bar */}
        <Box
          sx={{
            pt: 5,
            px: 3,
            pb: 1,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            bgcolor: 'white',
            flexShrink: 0,
          }}
        >
          <Typography variant="caption" sx={{ fontWeight: 600 }}>
            9:41
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
            <Box sx={{ fontSize: 12 }}>•••</Box>
            <Box sx={{ fontSize: 12 }}>📶</Box>
            <Box sx={{ fontSize: 12 }}>🔋</Box>
          </Box>
        </Box>

        {/* App Header */}
        <Box sx={{ 
          bgcolor: 'white', 
          px: 2, 
          py: 1.5, 
          borderBottom: '1px solid #E5E5EA', 
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <IconButton sx={{ color: '#007AFF', p: 0.5 }}>
            <Box sx={{ fontSize: 20 }}>‹</Box>
          </IconButton>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.125rem' }}>
            Your transactions
          </Typography>
          <Box sx={{ width: 32 }} />
        </Box>

        {/* Search Bar with Close button */}
        <Box sx={{ bgcolor: 'white', px: 2, py: 1.5, flexShrink: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Box 
              sx={{ 
                flex: 1,
                bgcolor: '#F2F2F7',
                borderRadius: 2,
                px: 1.5,
                py: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                border: '2px solid transparent',
                transition: 'all 0.2s',
                ...(result && {
                  borderColor: '#007AFF',
                  bgcolor: 'white',
                }),
              }}
            >
              <SearchIcon sx={{ fontSize: 18, color: '#8E8E93' }} />
              <input
                type="text"
                value={result?.query || searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Starbucks"
                style={{
                  border: 'none',
                  background: 'transparent',
                  outline: 'none',
                  flex: 1,
                  fontSize: '0.875rem',
                  color: '#3C3C43',
                  fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
                }}
              />
              {(result?.query || searchValue) && (
                <IconButton size="small" sx={{ p: 0.25 }} onClick={() => { setSearchValue(''); setShowDetails(false); }}>
                  <Box sx={{ fontSize: 16, color: '#8E8E93' }}>✕</Box>
                </IconButton>
              )}
            </Box>
            {result && (
              <Button 
                variant="text" 
                sx={{ 
                  color: '#007AFF',
                  textTransform: 'none',
                  fontSize: '0.9375rem',
                  minWidth: 'auto',
                  p: 0.5,
                }}
                onClick={() => {}}
              >
                Close
              </Button>
            )}
          </Stack>
        </Box>

        {/* Intelligence Response Card - Matching Reference */}
        {result && (() => {
          const insight = generateIntelligentInsight();
          const query = result.query.toLowerCase();
          
          if (insight && (query.includes('starbucks') || query.includes('dunkin'))) {
            return (
              <Box sx={{ bgcolor: 'white', flexShrink: 0 }}>
                {/* Merchant Badge */}
                <Box sx={{ px: 2, pt: 2, pb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ 
                      width: 36, 
                      height: 36, 
                      borderRadius: 1.5,
                      bgcolor: insight.logo?.bg || '#F2F2F7',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {insight.logo?.isIcon ? (
                        <Box sx={{ fontSize: 20, color: insight.logo?.color || '#000' }}>{insight.logo?.text}</Box>
                      ) : (
                        <Typography sx={{ color: insight.logo?.color || '#000', fontSize: '0.875rem', fontWeight: 700 }}>
                          {insight.logo?.text}
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500, fontSize: '1rem' }}>
                      {insight.merchant}
                    </Typography>
                  </Box>
                </Box>

                {/* Intelligence Summary Card */}
                <Box sx={{ px: 2, pb: 2 }}>
                  <Box sx={{ 
                    p: 2, 
                    bgcolor: '#F2F2F7',
                    borderRadius: 2,
                  }}>
                    <Stack direction="row" spacing={1.5}>
                      <Box sx={{ 
                        width: 40, 
                        height: 40, 
                        borderRadius: 1.5,
                        bgcolor: insight.logo?.bg || '#F2F2F7',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        {insight.logo?.isIcon ? (
                          <Box sx={{ fontSize: 20, color: insight.logo?.color || '#000' }}>{insight.logo?.text}</Box>
                        ) : (
                          <Typography sx={{ color: insight.logo?.color || '#000', fontSize: '0.875rem', fontWeight: 700 }}>
                            {insight.logo?.text}
                          </Typography>
                        )}
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ fontSize: '0.875rem', color: '#3C3C43', lineHeight: 1.5 }}>
                          {insight.summary}
                        </Typography>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: '#8E8E93', 
                            fontSize: '0.8125rem',
                            display: 'block',
                            mt: 1,
                          }}
                        >
                          {insight.viewText}
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>
                </Box>
              </Box>
            );
          } else if (insight) {
            // Default Intelligence Response
            return (
              <Box sx={{ bgcolor: 'white', flexShrink: 0 }}>
                {/* Intelligence Summary */}
                <Box sx={{ px: 2, py: 2 }}>
                  <Box sx={{ 
                    p: 2, 
                    bgcolor: '#F2F2F7',
                    borderRadius: 2,
                  }}>
                    <Stack direction="row" spacing={1.5}>
                      <Box sx={{ 
                        width: 40, 
                        height: 40, 
                        borderRadius: 1.5,
                        background: `linear-gradient(135deg, #5E5CE6 0%, #BF5AF2 50%, #FF375F 100%)`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        <AutoAwesomeIcon sx={{ fontSize: 20, color: 'white' }} />
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ fontSize: '0.875rem', color: '#3C3C43', lineHeight: 1.5 }}>
                          {insight.summary}
                        </Typography>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: '#8E8E93', 
                            fontSize: '0.8125rem',
                            display: 'block',
                            mt: 1,
                          }}
                        >
                          {insight.viewText}
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>
                </Box>
              </Box>
            );
          }
          return null;
        })()}

        {/* Related Transactions Header */}
        {result && transactions.length > 0 && (
          <Box sx={{ 
            bgcolor: '#F2F2F7', 
            px: 2, 
            py: 1.5, 
            flexShrink: 0,
          }}>
            <Typography variant="subtitle2" sx={{ 
              fontWeight: 600, 
              fontSize: '0.875rem',
              color: '#1C1C1E',
            }}>
              Related Transactions
            </Typography>
          </Box>
        )}

        {/* Transaction List */}
        <Box sx={{ 
          flex: 1, 
          overflowY: 'auto', 
          bgcolor: result ? 'white' : '#F2F2F7',
          minHeight: 0,
          WebkitOverflowScrolling: 'touch',
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#C7C7CC',
            borderRadius: '3px',
          },
        }}>
          {/* Transaction Groups */}
          {transactions.length > 0 ? (
            <>
              {result ? (
                // Show related transactions without date grouping for search results
                <Box sx={{ bgcolor: 'white' }}>
                  {transactions.map((transaction: any, index: number) => {
                    const logo = getMerchantLogo(transaction.name);
                    return (
                      <Box 
                        key={index}
                        onClick={() => {
                          setSelectedTransaction(transaction);
                          setShowDetails(true);
                        }}
                        sx={{ 
                          px: 2, 
                          py: 1.5, 
                          display: 'flex', 
                          alignItems: 'center',
                          cursor: 'pointer',
                          borderBottom: index === transactions.length - 1 ? 'none' : '1px solid #F2F2F7',
                          '&:hover': {
                            bgcolor: '#F9F9FB',
                          },
                        }}
                      >
                        <Box sx={{ 
                          width: 40, 
                          height: 40, 
                          borderRadius: 2,
                          bgcolor: logo.bg,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mr: 1.5,
                        }}>
                          {logo.isIcon ? (
                            <Box sx={{ fontSize: 20, color: logo.color }}>{logo.text}</Box>
                          ) : (
                            <Typography sx={{ color: logo.color, fontSize: '0.875rem', fontWeight: 700 }}>
                              {logo.text}
                            </Typography>
                          )}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.9375rem' }}>
                            {transaction.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#8E8E93', fontSize: '0.8125rem' }}>
                            {transaction.date} • {transaction.category}
                          </Typography>
                        </Box>
                        <Typography 
                          variant="subtitle2" 
                          sx={{ 
                            fontWeight: 600, 
                            fontSize: '0.9375rem',
                            color: transaction.amount > 0 ? '#34C759' : '#1C1C1E',
                          }}
                        >
                          {transaction.amount > 0 ? '+' : ''}{transaction.amount > 0 ? `$${transaction.amount.toFixed(2)}` : `-$${Math.abs(transaction.amount).toFixed(2)}`}
                        </Typography>
                      </Box>
                    );
                  })}
                </Box>
              ) : (
                // Show all transactions with date grouping when no search
                Object.entries(groupedTransactions).map(([date, dateTransactions]: [string, any]) => (
                  <Box key={date}>
                    <Typography variant="caption" sx={{ px: 2, py: 1, display: 'block', color: '#8E8E93', bgcolor: '#F2F2F7' }}>
                      {date}
                    </Typography>
                    
                    {/* Transaction Items */}
                    {dateTransactions.map((transaction: any, index: number) => {
                      const logo = getMerchantLogo(transaction.name);
                      return (
                        <Box 
                          key={index}
                          onClick={() => {
                            setSelectedTransaction(transaction);
                            setShowDetails(true);
                          }}
                          sx={{ 
                            bgcolor: 'white', 
                            px: 2, 
                            py: 1.5, 
                            display: 'flex', 
                            alignItems: 'center',
                            cursor: 'pointer',
                            borderBottom: index === dateTransactions.length - 1 ? 'none' : '1px solid #F2F2F7',
                            '&:hover': {
                              bgcolor: '#F9F9FB',
                            },
                          }}
                        >
                          <Box sx={{ 
                            width: 40, 
                            height: 40, 
                            borderRadius: 2,
                            bgcolor: logo.bg,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mr: 1.5,
                          }}>
                            {logo.isIcon ? (
                              <Box sx={{ fontSize: 20, color: logo.color }}>{logo.text}</Box>
                            ) : (
                              <Typography sx={{ color: logo.color, fontSize: '0.875rem', fontWeight: 700 }}>
                                {logo.text}
                              </Typography>
                            )}
                          </Box>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.9375rem' }}>
                              {transaction.name}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#8E8E93', fontSize: '0.8125rem' }}>
                              {transaction.category}
                            </Typography>
                          </Box>
                          <Typography 
                            variant="subtitle2" 
                            sx={{ 
                              fontWeight: 600, 
                              fontSize: '0.9375rem',
                              color: transaction.amount > 0 ? '#34C759' : '#1C1C1E',
                            }}
                          >
                            {transaction.amount > 0 ? '+' : ''}{transaction.amount > 0 ? `$${transaction.amount.toFixed(2)}` : `-$${Math.abs(transaction.amount).toFixed(2)}`}
                          </Typography>
                        </Box>
                      );
                    })}
                  </Box>
                ))
              )}
              {/* Extra padding at bottom for better scrolling */}
              <Box sx={{ height: 80 }} />
            </>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: '#8E8E93' }}>
                No transactions found
              </Typography>
            </Box>
          )}
        </Box>

        {/* Transaction Details Modal */}
        {showDetails && selectedTransaction && (
          <Box
            sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              bgcolor: 'white',
              borderTopLeftRadius: 3,
              borderTopRightRadius: 3,
              boxShadow: '0 -10px 40px rgba(0,0,0,0.1)',
              p: 3,
              maxHeight: '70%',
              animation: 'slideUp 0.3s ease-out',
              '@keyframes slideUp': {
                from: { transform: 'translateY(100%)' },
                to: { transform: 'translateY(0)' },
              },
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <IconButton size="small" onClick={() => setShowDetails(false)}>
                <Box sx={{ fontSize: 20, color: '#8E8E93' }}>✕</Box>
              </IconButton>
            </Box>
            
            {(() => {
              const logo = getMerchantLogo(selectedTransaction.name);
              return (
                <>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                    <Box sx={{ 
                      width: 60, 
                      height: 60, 
                      borderRadius: 2,
                      bgcolor: logo.bg,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}>
                      {logo.isIcon ? (
                        <Box sx={{ fontSize: 32, color: logo.color }}>{logo.text}</Box>
                      ) : (
                        <Typography sx={{ color: logo.color, fontSize: '1.5rem', fontWeight: 700 }}>
                          {logo.text}
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>{selectedTransaction.name}</Typography>
                    {selectedTransaction.location && (
                      <Typography variant="caption" sx={{ color: '#8E8E93', fontSize: '0.75rem' }}>
                        {selectedTransaction.location}
                      </Typography>
                    )}
                    <Typography variant="h4" sx={{ fontWeight: 600, mt: 1 }}>
                      {selectedTransaction.amount > 0 ? '+' : ''}{selectedTransaction.amount > 0 ? `$${selectedTransaction.amount.toFixed(2)}` : `-$${Math.abs(selectedTransaction.amount).toFixed(2)}`}
                    </Typography>
                  </Box>

                  <Stack spacing={2}>
                    <Stack direction="row" spacing={1}>
                      <Chip label={selectedTransaction.category} size="small" sx={{ bgcolor: '#F2F2F7' }} />
                      {selectedTransaction.category.includes('Coffee') && (
                        <Chip label="Coffee" size="small" sx={{ bgcolor: '#F2F2F7' }} />
                      )}
                    </Stack>
                    
                    <Divider />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ color: '#8E8E93' }}>Date</Typography>
                      <Typography variant="body2">{selectedTransaction.date}</Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ color: '#8E8E93' }}>Type</Typography>
                      <Typography variant="body2">{selectedTransaction.amount > 0 ? 'Credit' : 'Debit'}</Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ color: '#8E8E93' }}>Status</Typography>
                      <Typography variant="body2">{selectedTransaction.status || 'Booked'}</Typography>
                    </Box>
                    
                    {selectedTransaction.location && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" sx={{ color: '#8E8E93' }}>Location</Typography>
                        <Typography variant="body2">{selectedTransaction.location}</Typography>
                      </Box>
                    )}
                  </Stack>
                </>
              );
            })()}
          </Box>
        )}
      </Box>
    </Box>
  );
};

const PlaygroundApple: React.FC = () => {
  // const theme = useTheme();
  const [query, setQuery] = useState('');
  const [cif, setCif] = useState('CIF00000001');
  const [showCitations, setShowCitations] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);

  const searchMutation = useMutation({
    mutationFn: searchApi.magicSearch,
    onSuccess: (data) => {
      setResult(data);
      // Automatically expand citations/transactions if transactions are available
      setShowCitations(!!data.transactions && data.transactions.length > 0);
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

  const suggestions = [
    { icon: <TipsIcon />, text: "Show my spending trends" },
    { icon: <LightbulbIcon />, text: "Analyze my largest transactions" },
    { icon: <PsychologyIcon />, text: "What are my saving patterns?" },
  ];

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        background: `linear-gradient(180deg, ${appleColors.neutral[50]} 0%, ${alpha(appleColors.primary.main, 0.02)} 100%)`,
      }}
    >
      <Container maxWidth="xl" sx={{ py: 5 }}>
        {/* Header */}
        <Fade in={true} timeout={600}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
              <BrandLogo size="large" showPlayground={true} />
            </Box>
            <Typography variant="body1" color="text.secondary">
              Experience the power of AI-driven insights with natural language
            </Typography>
          </Box>
        </Fade>

        <Grid container spacing={4}>
          {/* Main Content */}
          <Grid item xs={12} lg={7}>
            <Stack spacing={3}>
              {/* Search Card */}
              <Fade in={true} timeout={800}>
                <div>
                  <GlassCard sx={{ p: 4 }}>
                    <form onSubmit={handleSubmit}>
                    <Stack spacing={3}>
                      {/* Customer Selector */}
                      <FormControl fullWidth>
                        <InputLabel
                          sx={{
                            '&.Mui-focused': {
                              color: appleColors.primary.main,
                            },
                          }}
                        >
                          Customer Profile
                        </InputLabel>
                        <Select
                          value={cif}
                          onChange={(e) => setCif(e.target.value)}
                          label="Customer Profile"
                          sx={{
                            borderRadius: `${appleBorderRadius.md}px`,
                            '& .MuiOutlinedInput-notchedOutline': {
                              borderColor: appleColors.neutral[200],
                            },
                          }}
                        >
                          {[...Array(20)].map((_, i) => (
                            <MenuItem key={i} value={`CIF${String(i + 1).padStart(8, '0')}`}>
                              Customer {i + 1} • CIF{String(i + 1).padStart(8, '0')}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      {/* Query Input */}
                      <Box>
                        <TextField
                          fullWidth
                          multiline
                          rows={3}
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="Ask me anything about your financial data..."
                          variant="outlined"
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: `${appleBorderRadius.md}px`,
                              backgroundColor: appleColors.neutral[50],
                              fontSize: '1.1rem',
                              '&.Mui-focused': {
                                backgroundColor: '#FFFFFF',
                                boxShadow: `0 0 0 4px ${alpha(appleColors.primary.main, 0.1)}`,
                              },
                            },
                          }}
                        />
                      </Box>

                      {/* Suggestions */}
                      {!result && (
                        <Box>
                          <Typography variant="caption" color="text.secondary" sx={{ mb: 1.5, display: 'block' }}>
                            Try asking:
                          </Typography>
                          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                            {suggestions.map((suggestion, index) => (
                              <Chip
                                key={index}
                                icon={suggestion.icon}
                                label={suggestion.text}
                                onClick={() => setQuery(suggestion.text)}
                                sx={{
                                  cursor: 'pointer',
                                  backgroundColor: appleColors.neutral[100],
                                  transition: 'all 0.2s ease',
                                  '&:hover': {
                                    backgroundColor: alpha(appleColors.primary.main, 0.1),
                                    transform: 'translateY(-2px)',
                                  },
                                }}
                              />
                            ))}
                          </Stack>
                        </Box>
                      )}

                      {/* Submit Button */}
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        fullWidth
                        disabled={searchMutation.isPending || !query.trim()}
                        endIcon={!searchMutation.isPending && <ArrowForwardIcon />}
                        sx={{
                          py: 1.75,
                          borderRadius: appleBorderRadius.pill,
                          fontSize: '1rem',
                          fontWeight: 600,
                          background: searchMutation.isPending
                            ? appleColors.neutral[200]
                            : `linear-gradient(135deg, ${appleColors.primary.main} 0%, ${appleColors.accent.purple} 100%)`,
                          boxShadow: searchMutation.isPending
                            ? 'none'
                            : `0 8px 24px ${alpha(appleColors.primary.main, 0.25)}`,
                          '&:hover': {
                            boxShadow: `0 12px 32px ${alpha(appleColors.primary.main, 0.35)}`,
                          },
                        }}
                      >
                        {searchMutation.isPending ? (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CircularProgress size={20} color="inherit" />
                            Thinking...
                          </Box>
                        ) : (
                          'Ask Wondr'
                        )}
                      </Button>
                    </Stack>
                  </form>
                </GlassCard>
                </div>
              </Fade>

              {/* Loading State */}
              {searchMutation.isPending && (
                <Fade in={true}>
                  <div>
                    <GlassCard sx={{ p: 4 }}>
                      <Stack spacing={3}>
                        <Skeleton variant="rounded" height={20} width="60%" />
                        <Skeleton variant="rounded" height={60} />
                        <Skeleton variant="rounded" height={20} width="40%" />
                      </Stack>
                    </GlassCard>
                  </div>
                </Fade>
              )}

              {/* Error State */}
              {searchMutation.isError && (
                <Fade in={true}>
                  <Alert
                    severity="error"
                    sx={{
                      borderRadius: `${appleBorderRadius.md}px`,
                      backgroundColor: alpha(appleColors.semantic.error, 0.1),
                      border: `1px solid ${alpha(appleColors.semantic.error, 0.2)}`,
                    }}
                  >
                    Unable to process your request. Please try again.
                  </Alert>
                </Fade>
              )}

              {/* Results */}
              {result && !searchMutation.isPending && (
                <Fade in={true}>
                  <div>
                    <GlassCard sx={{ overflow: 'hidden' }}>
                    {/* Result Header */}
                    <Box
                      sx={{
                        p: 3,
                        background: `linear-gradient(135deg, ${alpha(appleColors.primary.main, 0.05)} 0%, ${alpha(appleColors.accent.purple, 0.05)} 100%)`,
                        borderBottom: `1px solid ${appleColors.neutral[200]}`,
                      }}
                    >
                      <Stack direction="row" alignItems="center" justifyContent="space-between">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <CheckCircleIcon sx={{ color: appleColors.semantic.success }} />
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            Intelligence Response
                          </Typography>
                        </Box>
                        <Stack direction="row" spacing={1}>
                          <Chip
                            icon={<TimerIcon />}
                            label={`${result.latency_ms}ms`}
                            size="small"
                            sx={{ backgroundColor: appleColors.neutral[100] }}
                          />
                          <Chip
                            icon={<DataObjectIcon />}
                            label={result.model_used}
                            size="small"
                            sx={{ backgroundColor: appleColors.neutral[100] }}
                          />
                        </Stack>
                      </Stack>
                    </Box>

                    {/* Compact Answer with inline sources */}
                    <Box sx={{ p: 2.5 }}>
                      <Stack direction="row" spacing={2}>
                        <Box sx={{ flex: 1 }}>
                          <Typography
                            variant="body1"
                            sx={{
                              lineHeight: 1.6,
                              color: appleColors.neutral[800],
                              fontSize: '0.9375rem',
                              fontWeight: 500,
                            }}
                          >
                            {result.answer}
                          </Typography>
                        </Box>
                        
                        {/* Compact Sources Preview */}
                        <Box sx={{ width: 120, flexShrink: 0 }}>
                          <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 1 }}>
                            <Typography variant="caption" sx={{ color: appleColors.neutral[500], display: 'block' }}>
                              Sources ({result.transactions ? result.transactions.length + ' transactions' : result.citations.length})
                            </Typography>
                            {showCitations && result.transactions && (
                              <Typography variant="caption" sx={{ color: appleColors.accent.green, fontSize: '0.6rem', fontWeight: 600 }}>
                                ✓ Expanded
                              </Typography>
                            )}
                          </Stack>
                          {/* Only show preview if not already expanded */}
                          {!showCitations && (
                            <Stack spacing={0.5}>
                              {/* Show transactions if available, otherwise show citations */}
                              {result.transactions ? (
                                <>
                                  <Box
                                    sx={{
                                      p: 0.75,
                                      borderRadius: 1,
                                      bgcolor: alpha(appleColors.primary.main, 0.05),
                                      cursor: 'pointer',
                                      transition: 'all 0.2s',
                                      '&:hover': {
                                        bgcolor: alpha(appleColors.primary.main, 0.1),
                                      },
                                    }}
                                    onClick={() => setShowCitations(true)}
                                  >
                                    <Typography 
                                      variant="caption" 
                                      sx={{ 
                                        fontSize: '0.7rem',
                                        color: appleColors.primary.main,
                                        display: 'block',
                                        textAlign: 'center',
                                      }}
                                    >
                                      View {result.transactions.length} transactions
                                    </Typography>
                                  </Box>
                                </>
                              ) : (
                              <>
                                {result.citations.slice(0, 3).map((citation, index) => (
                                  <Box
                                    key={index}
                                    sx={{
                                      p: 0.75,
                                      borderRadius: 1,
                                      bgcolor: alpha(appleColors.primary.main, 0.05),
                                      cursor: 'pointer',
                                      transition: 'all 0.2s',
                                      '&:hover': {
                                        bgcolor: alpha(appleColors.primary.main, 0.1),
                                      },
                                    }}
                                    onClick={() => setShowCitations(!showCitations)}
                                  >
                                    <Typography 
                                      variant="caption" 
                                      sx={{ 
                                        fontSize: '0.625rem',
                                        color: appleColors.primary.main,
                                        display: 'block',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                      }}
                                    >
                                      {citation.source === 'cif' ? '📊' : '📚'} {citation.title}
                                    </Typography>
                                  </Box>
                                ))}
                                {result.citations.length > 3 && (
                                  <Button
                                    size="small"
                                    onClick={() => setShowCitations(!showCitations)}
                                    sx={{
                                      fontSize: '0.625rem',
                                      textTransform: 'none',
                                      p: 0.5,
                                      minWidth: 0,
                                    }}
                                  >
                                    +{result.citations.length - 3} more
                                  </Button>
                                )}
                              </>
                            )}
                            </Stack>
                          )}
                        </Box>
                      </Stack>

                      {/* Expandable Sources */}
                      <Collapse in={showCitations}>
                        <Divider sx={{ my: 2, borderColor: appleColors.neutral[200] }} />
                        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
                          {result.transactions ? 'Transaction Details' : 'Supporting Documents'}
                        </Typography>
                        <Stack spacing={1.5}>
                          {/* Show transaction cards if available */}
                          {result.transactions ? (
                            <>
                              {result.transactions.map((transaction, index) => (
                                <Box
                                  key={index}
                                  sx={{
                                    p: 2,
                                    borderRadius: 2,
                                    background: appleColors.glass.ultraLight,
                                    border: `1px solid ${alpha(appleColors.neutral[200], 0.5)}`,
                                    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                                    cursor: 'pointer',
                                    '&:hover': {
                                      transform: 'translateY(-2px)',
                                      boxShadow: appleShadows.md,
                                      borderColor: appleColors.primary.main,
                                      background: 'white',
                                    },
                                  }}
                                >
                                  <Stack direction="row" spacing={2} alignItems="center">
                                    {/* Transaction Icon/Number */}
                                    <Box
                                      sx={{
                                        width: 48,
                                        height: 48,
                                        borderRadius: '50%',
                                        background: `linear-gradient(135deg, ${appleColors.primary.main} 0%, ${appleColors.primary.dark} 100%)`,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0,
                                        boxShadow: appleShadows.sm,
                                      }}
                                    >
                                      <Typography 
                                        sx={{ 
                                          color: 'white',
                                          fontSize: '1.2rem',
                                          fontWeight: 600
                                        }}
                                      >
                                        {transaction.merchant === 'None' ? '💱' : '💳'}
                                      </Typography>
                                    </Box>
                                    
                                    {/* Transaction Details */}
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                                        <Box>
                                          <Typography 
                                            variant="subtitle2" 
                                            sx={{ 
                                              fontWeight: 600, 
                                              fontSize: '0.9rem',
                                              color: appleColors.neutral[900],
                                              mb: 0.5
                                            }}
                                          >
                                            {transaction.merchant === 'None' ? 'Transfer' : transaction.merchant}
                                          </Typography>
                                          <Stack direction="row" spacing={1} alignItems="center">
                                            <Chip
                                              label={transaction.category}
                                              size="small"
                                              sx={{
                                                height: 22,
                                                fontSize: '0.7rem',
                                                fontWeight: 500,
                                                backgroundColor: alpha(appleColors.primary.main, 0.1),
                                                color: appleColors.primary.main,
                                                border: 'none',
                                              }}
                                            />
                                            <Typography 
                                              variant="caption" 
                                              sx={{ 
                                                color: appleColors.neutral[500],
                                                fontSize: '0.75rem'
                                              }}
                                            >
                                              {transaction.date}
                                            </Typography>
                                          </Stack>
                                        </Box>
                                        
                                        {/* Amount */}
                                        <Typography 
                                          variant="subtitle1" 
                                          sx={{ 
                                            fontWeight: 700,
                                            fontSize: '1rem',
                                            color: transaction.amount > 0 
                                              ? appleColors.accent.green 
                                              : appleColors.neutral[900],
                                          }}
                                        >
                                          {transaction.amount > 0 ? '+' : ''}
                                          Rp {Math.abs(transaction.amount).toLocaleString('id-ID', {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
                                          })}
                                        </Typography>
                                      </Stack>
                                    </Box>
                                  </Stack>
                                </Box>
                              ))}
                            </>
                          ) : (
                            <>
                              {/* Original citation cards */}
                              {result.citations.map((citation, index) => (
                                <Box
                                  key={index}
                                  sx={{
                                    p: 1.5,
                                    borderRadius: 2,
                                    border: `1px solid ${appleColors.neutral[200]}`,
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                      borderColor: appleColors.primary.main,
                                      bgcolor: alpha(appleColors.primary.main, 0.02),
                                    },
                                  }}
                                >
                                  <Stack direction="row" spacing={1.5}>
                                    <Box
                                      sx={{
                                        width: 32,
                                        height: 32,
                                        borderRadius: 1,
                                        backgroundColor: alpha(appleColors.primary.main, 0.1),
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0,
                                      }}
                                    >
                                      <Typography variant="caption" color="primary" sx={{ fontWeight: 600 }}>
                                        {index + 1}
                                      </Typography>
                                    </Box>
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                      <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.8125rem', mb: 0.25 }}>
                                        {citation.title}
                                      </Typography>
                                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem', mb: 0.75, lineHeight: 1.4 }}>
                                        {citation.text_snippet}
                                      </Typography>
                                      <Stack direction="row" spacing={0.5}>
                                        <Chip
                                          label={citation.source === 'cif' ? 'Transaction' : 'Knowledge'}
                                          size="small"
                                          sx={{
                                            height: 20,
                                            fontSize: '0.625rem',
                                            backgroundColor: alpha(
                                              citation.source === 'cif'
                                                ? appleColors.accent.green
                                                : appleColors.accent.orange,
                                              0.1
                                            ),
                                            color:
                                              citation.source === 'cif'
                                                ? appleColors.accent.green
                                                : appleColors.accent.orange,
                                          }}
                                        />
                                        <Chip
                                          label={`${(citation.similarity_score * 100).toFixed(0)}%`}
                                          size="small"
                                          sx={{
                                            height: 20,
                                            fontSize: '0.625rem',
                                            backgroundColor: appleColors.neutral[100],
                                          }}
                                        />
                                      </Stack>
                                    </Box>
                                  </Stack>
                                </Box>
                              ))}
                            </>
                          )}
                        </Stack>
                      </Collapse>
                    </Box>
                  </GlassCard>
                  </div>
                </Fade>
              )}
            </Stack>
          </Grid>

          {/* Mobile Preview */}
          <Grid item xs={12} lg={5}>
            <Fade in={true} timeout={1000}>
              <Box
                sx={{
                  position: 'sticky',
                  top: 80,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 3 }}>
                  Mobile Experience Preview
                </Typography>
                <AppleMobilePreview result={result || undefined} />
              </Box>
            </Fade>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default PlaygroundApple;