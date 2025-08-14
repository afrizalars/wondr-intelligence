import React from 'react';
import { Box, Typography } from '@mui/material';
import { appleColors } from '../theme/appleTheme';

interface BrandLogoProps {
  size?: 'small' | 'medium' | 'large';
  showPlayground?: boolean;
  showByBNI?: boolean;
  animateIntelligence?: boolean;
}

const BrandLogo: React.FC<BrandLogoProps> = ({ 
  size = 'medium', 
  showPlayground = false,
  showByBNI = false,
  animateIntelligence = true
}) => {
  const sizes = {
    small: {
      fontSize: '1.125rem',
      underlineWidth: 20,
      underlineHeight: 3,
      gap: 0.5,
    },
    medium: {
      fontSize: '1.75rem',
      underlineWidth: 32,
      underlineHeight: 4,
      gap: 0.75,
    },
    large: {
      fontSize: '2.75rem',
      underlineWidth: 50,
      underlineHeight: 6,
      gap: 1,
    },
  };

  const currentSize = sizes[size];
  
  // Wondr brand orange color
  const wondrOrange = '#FF8A00';
  const wondrTeal = '#4ECDC4';

  return (
    <Box sx={{ display: 'flex', alignItems: 'baseline', gap: currentSize.gap }}>
      {/* Wondr with underline */}
      <Box sx={{ position: 'relative', display: 'inline-block' }}>
        <Typography
          sx={{
            fontWeight: 800,
            fontSize: currentSize.fontSize,
            letterSpacing: '-0.04em',
            color: wondrOrange,
            fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
          }}
        >
          wondr
        </Typography>
        {/* Teal underline */}
        <Box
          sx={{
            position: 'absolute',
            bottom: size === 'large' ? -8 : -4,
            left: '50%',
            transform: 'translateX(-50%)',
            width: currentSize.underlineWidth,
            height: currentSize.underlineHeight,
            backgroundColor: wondrTeal,
            borderRadius: 1,
          }}
        />
      </Box>
      
      {/* Intelligence in Apple Intelligence style with gradient */}
      <Typography
        sx={{
          fontWeight: 400,
          fontSize: currentSize.fontSize,
          letterSpacing: '-0.02em',
          fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
          ml: size === 'large' ? 1 : 0.5,
          background: `linear-gradient(90deg, 
            #5E5CE6 0%, 
            #BF5AF2 25%, 
            #FF375F 50%, 
            #FF9F0A 75%, 
            #30D158 100%)`,
          backgroundSize: animateIntelligence ? '200% auto' : '100% auto',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          animation: animateIntelligence ? 'intelligenceGradient 5s ease infinite' : 'none',
          '@keyframes intelligenceGradient': {
            '0%': { backgroundPosition: '0% 50%' },
            '50%': { backgroundPosition: '100% 50%' },
            '100%': { backgroundPosition: '0% 50%' },
          },
        }}
      >
        Intelligence
      </Typography>
      
      {/* Playground text if needed */}
      {showPlayground && (
        <Typography
          sx={{
            fontWeight: 300,
            fontSize: currentSize.fontSize,
            letterSpacing: '-0.03em',
            fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
            background: `linear-gradient(90deg, 
              ${appleColors.neutral[500]} 0%, 
              ${appleColors.neutral[400]} 100%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Playground
        </Typography>
      )}
      
      {/* by BNI text if needed */}
      {showByBNI && (
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.3, ml: 1 }}>
          <Typography
            sx={{
              fontSize: size === 'large' ? '1.25rem' : '0.875rem',
              color: appleColors.neutral[500],
              fontWeight: 400,
              fontFamily: '"SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif',
            }}
          >
            by
          </Typography>
          <Typography
            sx={{
              fontSize: size === 'large' ? '1.25rem' : '0.875rem',
              color: appleColors.neutral[600],
              fontWeight: 600,
              fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
            }}
          >
            BNI
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default BrandLogo;