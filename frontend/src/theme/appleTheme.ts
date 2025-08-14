import { createTheme, alpha } from '@mui/material/styles';

// Apple Intelligence Color Palette
const colors = {
  // Primary colors - soft blue spectrum
  primary: {
    main: '#007AFF',      // iOS blue
    light: '#5AC8FA',     // Light blue
    dark: '#0051D5',      // Deep blue
    contrastText: '#FFFFFF',
  },
  
  // Neutral grays - Apple's signature palette
  neutral: {
    50: '#FBFBFD',       // Off-white
    100: '#F7F7F9',      // Light gray
    200: '#F2F2F7',      // System gray 6
    300: '#E5E5EA',      // System gray 5
    400: '#D1D1D6',      // System gray 4
    500: '#C7C7CC',      // System gray 3
    600: '#8E8E93',      // System gray 2
    700: '#636366',      // System gray
    800: '#48484A',      // Dark gray
    900: '#2C2C2E',      // Almost black
    950: '#1C1C1E',      // True black
  },
  
  // Accent colors - muted pastels
  accent: {
    purple: '#AF52DE',    // iOS purple
    pink: '#FF2D55',      // iOS pink
    orange: '#FF9500',    // iOS orange
    yellow: '#FFCC00',    // iOS yellow
    green: '#34C759',     // iOS green
    teal: '#5AC8FA',      // iOS teal
    indigo: '#5856D6',    // iOS indigo
  },
  
  // Semantic colors
  semantic: {
    success: '#34C759',
    warning: '#FF9500',
    error: '#FF3B30',
    info: '#5AC8FA',
  },
  
  // Glass morphism
  glass: {
    light: 'rgba(255, 255, 255, 0.72)',
    medium: 'rgba(255, 255, 255, 0.5)',
    dark: 'rgba(255, 255, 255, 0.25)',
    ultraLight: 'rgba(255, 255, 255, 0.85)',
  },
  
  // Backdrop filters
  blur: {
    light: 'blur(20px)',
    medium: 'blur(40px)',
    heavy: 'blur(80px)',
  },
};

// Typography scale following SF Pro
const typography = {
  fontFamily: [
    '-apple-system',
    'BlinkMacSystemFont',
    '"SF Pro Display"',
    '"SF Pro Text"',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
  ].join(','),
  
  h1: {
    fontSize: '3rem',
    fontWeight: 700,
    letterSpacing: '-0.025em',
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2.25rem',
    fontWeight: 600,
    letterSpacing: '-0.02em',
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.875rem',
    fontWeight: 600,
    letterSpacing: '-0.015em',
    lineHeight: 1.35,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 600,
    letterSpacing: '-0.01em',
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 600,
    letterSpacing: '-0.005em',
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '1.125rem',
    fontWeight: 600,
    letterSpacing: '0',
    lineHeight: 1.5,
  },
  subtitle1: {
    fontSize: '1.0625rem',
    fontWeight: 500,
    letterSpacing: '0',
    lineHeight: 1.5,
  },
  subtitle2: {
    fontSize: '0.9375rem',
    fontWeight: 500,
    letterSpacing: '0.005em',
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    letterSpacing: '0',
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    letterSpacing: '0.01em',
    lineHeight: 1.5,
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    letterSpacing: '0.02em',
    lineHeight: 1.4,
  },
  button: {
    fontSize: '0.9375rem',
    fontWeight: 500,
    letterSpacing: '0.01em',
    textTransform: 'none' as const,
  },
};

// Spacing system (8px base)
const spacing = 8;

// Border radius system
const borderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  pill: 9999,
};

// Shadows - very subtle
const shadows = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
  sm: '0 2px 4px 0 rgba(0, 0, 0, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.02)',
  md: '0 4px 8px 0 rgba(0, 0, 0, 0.04), 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
  lg: '0 8px 16px 0 rgba(0, 0, 0, 0.04), 0 4px 8px 0 rgba(0, 0, 0, 0.02)',
  xl: '0 16px 32px 0 rgba(0, 0, 0, 0.06), 0 8px 16px 0 rgba(0, 0, 0, 0.03)',
  xxl: '0 24px 48px 0 rgba(0, 0, 0, 0.08), 0 12px 24px 0 rgba(0, 0, 0, 0.04)',
  glass: '0 8px 32px 0 rgba(31, 38, 135, 0.1)',
};

// Transitions
const transitions = {
  duration: {
    shortest: 150,
    shorter: 200,
    short: 250,
    standard: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195,
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    spring: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
};

// Create the theme
const appleTheme = createTheme({
  palette: {
    mode: 'light',
    primary: colors.primary,
    secondary: {
      main: colors.accent.purple,
      light: alpha(colors.accent.purple, 0.3),
      dark: colors.accent.indigo,
    },
    error: {
      main: colors.semantic.error,
    },
    warning: {
      main: colors.semantic.warning,
    },
    info: {
      main: colors.semantic.info,
    },
    success: {
      main: colors.semantic.success,
    },
    grey: colors.neutral,
    background: {
      default: colors.neutral[50],
      paper: '#FFFFFF',
    },
    text: {
      primary: colors.neutral[950],
      secondary: colors.neutral[600],
      disabled: colors.neutral[400],
    },
    divider: alpha(colors.neutral[400], 0.2),
  },
  
  typography,
  spacing,
  
  shape: {
    borderRadius: borderRadius.md,
  },
  
  shadows: [
    'none',
    shadows.xs,
    shadows.sm,
    shadows.sm,
    shadows.md,
    shadows.md,
    shadows.md,
    shadows.lg,
    shadows.lg,
    shadows.lg,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.xxl,
    shadows.glass,
  ],
  
  transitions,
  
  components: {
    // Button component
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.pill,
          textTransform: 'none' as const,
          fontWeight: 500,
          padding: '10px 20px',
          transition: 'all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: shadows.sm,
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: `linear-gradient(135deg, ${colors.primary.main} 0%, ${colors.primary.light} 100%)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${colors.primary.dark} 0%, ${colors.primary.main} 100%)`,
          },
        },
        outlined: {
          borderColor: colors.neutral[300],
          color: colors.neutral[700],
          '&:hover': {
            borderColor: colors.primary.main,
            backgroundColor: alpha(colors.primary.main, 0.04),
          },
        },
      },
    },
    
    // Paper component
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.lg,
          boxShadow: shadows.sm,
          border: `1px solid ${alpha(colors.neutral[200], 0.5)}`,
          backgroundImage: 'none',
          backgroundColor: '#FFFFFF',
          backdropFilter: 'blur(20px)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: shadows.md,
          },
        },
        elevation0: {
          boxShadow: 'none',
          border: `1px solid ${colors.neutral[200]}`,
        },
        elevation1: {
          boxShadow: shadows.sm,
        },
      },
    },
    
    // Card component
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.lg,
          boxShadow: shadows.sm,
          border: `1px solid ${alpha(colors.neutral[200], 0.3)}`,
          background: `linear-gradient(135deg, #FFFFFF 0%, ${colors.neutral[50]} 100%)`,
          transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: shadows.lg,
          },
        },
      },
    },
    
    // TextField component
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: borderRadius.md,
            backgroundColor: colors.neutral[50],
            transition: 'all 0.2s ease',
            '& fieldset': {
              borderColor: colors.neutral[200],
              borderWidth: '1px',
            },
            '&:hover': {
              backgroundColor: '#FFFFFF',
              '& fieldset': {
                borderColor: colors.neutral[300],
              },
            },
            '&.Mui-focused': {
              backgroundColor: '#FFFFFF',
              boxShadow: `0 0 0 4px ${alpha(colors.primary.main, 0.1)}`,
              '& fieldset': {
                borderColor: colors.primary.main,
                borderWidth: '1px',
              },
            },
          },
        },
      },
    },
    
    // Chip component
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.pill,
          fontWeight: 500,
          border: 'none',
          transition: 'all 0.2s ease',
        },
        filled: {
          backgroundColor: colors.neutral[100],
          color: colors.neutral[700],
          '&:hover': {
            backgroundColor: colors.neutral[200],
          },
        },
        outlined: {
          borderColor: colors.neutral[300],
          backgroundColor: 'transparent',
          '&:hover': {
            backgroundColor: colors.neutral[50],
          },
        },
      },
    },
    
    // AppBar component
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderBottom: `1px solid ${colors.neutral[200]}`,
          backgroundColor: alpha('#FFFFFF', 0.8),
          backdropFilter: 'blur(20px)',
          color: colors.neutral[900],
        },
      },
    },
    
    // Drawer component
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: `1px solid ${colors.neutral[200]}`,
          backgroundColor: alpha(colors.neutral[50], 0.95),
          backdropFilter: 'blur(20px)',
        },
      },
    },
    
    // List components
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.md,
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.04),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(colors.primary.main, 0.08),
            '&:hover': {
              backgroundColor: alpha(colors.primary.main, 0.12),
            },
          },
        },
      },
    },
    
    // Table components
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottomColor: colors.neutral[200],
        },
        head: {
          backgroundColor: colors.neutral[50],
          fontWeight: 600,
          color: colors.neutral[600],
          fontSize: '0.875rem',
        },
      },
    },
    
    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: alpha(colors.primary.main, 0.02),
          },
          '&:nth-of-type(even)': {
            backgroundColor: colors.neutral[50],
          },
        },
      },
    },
    
    // Alert component
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.md,
          border: 'none',
        },
        standardSuccess: {
          backgroundColor: alpha(colors.semantic.success, 0.1),
          color: colors.semantic.success,
        },
        standardError: {
          backgroundColor: alpha(colors.semantic.error, 0.1),
          color: colors.semantic.error,
        },
        standardWarning: {
          backgroundColor: alpha(colors.semantic.warning, 0.1),
          color: colors.semantic.warning,
        },
        standardInfo: {
          backgroundColor: alpha(colors.semantic.info, 0.1),
          color: colors.semantic.info,
        },
      },
    },
    
    // Dialog component
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: borderRadius.xl,
          boxShadow: shadows.xxl,
        },
      },
    },
    
    // Menu component
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: borderRadius.md,
          boxShadow: shadows.lg,
          border: `1px solid ${colors.neutral[200]}`,
          marginTop: spacing,
        },
      },
    },
    
    // Select component
    MuiSelect: {
      styleOverrides: {
        select: {
          borderRadius: borderRadius.md,
        },
      },
    },
    
    // Avatar component
    MuiAvatar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.neutral[200],
          color: colors.neutral[700],
        },
        colorDefault: {
          backgroundColor: colors.neutral[100],
          color: colors.neutral[600],
        },
      },
    },
    
    // Divider component
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: colors.neutral[200],
        },
      },
    },
    
    // LinearProgress component
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.pill,
          height: 4,
          backgroundColor: colors.neutral[200],
        },
        bar: {
          borderRadius: borderRadius.pill,
          background: `linear-gradient(90deg, ${colors.primary.main} 0%, ${colors.primary.light} 100%)`,
        },
      },
    },
    
    // CircularProgress component
    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: colors.primary.main,
        },
      },
    },
    
    // Skeleton component
    MuiSkeleton: {
      styleOverrides: {
        root: {
          backgroundColor: colors.neutral[100],
          '&::after': {
            background: `linear-gradient(90deg, transparent, ${alpha(colors.neutral[200], 0.3)}, transparent)`,
          },
        },
      },
    },
  },
});

// Export custom properties
export const appleColors = colors;
export const appleBorderRadius = borderRadius;
export const appleShadows = shadows;
export const appleTransitions = transitions;

export default appleTheme;