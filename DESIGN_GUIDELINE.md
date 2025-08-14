# Design Guidelines - Wondr Intelligence

## Design Philosophy
Our design philosophy centers on creating an intuitive, elegant, and powerful financial intelligence platform that delivers a premium, executive-level user experience through sophisticated glassmorphic design and thoughtful microinteractions.

## Core Design Principles

### 1. Clarity
- **Hierarchy**: Clear visual hierarchy guides users through information
- **Typography**: Legible text at all sizes with appropriate contrast
- **Icons**: Simple, recognizable symbols that enhance understanding
- **Space**: Generous white space for clarity and executive readability

### 2. Deference
- **Content First**: UI elements complement, never compete with content
- **Subtle Chrome**: Interface elements fade when not in use
- **Depth**: Translucency and blurring create layered experiences
- **Motion**: Fluid animations that feel natural and purposeful

### 3. Depth
- **Layering**: Visual layers help users understand hierarchy
- **Shadows**: Soft shadows create realistic depth
- **Translucency**: Glass morphism effects for modern sophistication
- **Z-axis**: Strategic use of elevation for importance

## Design & Branding Guidelines

### Color Palette

#### Base Colors
```css
/* Foundation Colors */
--base-white: #F7F7F7;        /* Off-white */
--base-beige: #F0EDE8;        /* Soft beige */

/* Translucent Panels */
--panel-white-60: rgba(255, 255, 255, 0.6);
--panel-white-70: rgba(255, 255, 255, 0.7);
--panel-white-80: rgba(255, 255, 255, 0.8);
--panel-blur: blur(8px);

/* Accent Colors */
--accent-blue: #A4C8E7;       /* Pastel blue */
--accent-pink: #E7C8D2;       /* Blush pink */
--accent-mint: #C8E7D5;       /* Soft mint */
```

#### Supporting Colors
```css
/* Semantic Colors */
--success: #C8E7D5;           /* Soft mint for success */
--warning: #F5E6D3;           /* Soft peach for warnings */
--error: #E7C8D2;             /* Blush pink for errors */
--info: #A4C8E7;              /* Pastel blue for info */

/* Text Colors */
--text-primary: #2C2C2C;      /* High contrast dark */
--text-secondary: #5A5A5A;    /* Medium contrast */
--text-tertiary: #8A8A8A;     /* Low contrast */
--text-inverse: #FFFFFF;      /* White text on dark */
```

### Typography

```css
/* Headings */
--heading-font: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
--heading-weight: 700;         /* Bold */
--heading-size-lg: 32px;
--heading-size-md: 28px;
--heading-size-sm: 24px;

/* Subheadings */
--subheading-font: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
--subheading-weight: 500;      /* Medium */
--subheading-size-lg: 20px;
--subheading-size-sm: 18px;

/* Body Text */
--body-font: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
--body-weight: 400;            /* Regular */
--body-size: 16px;
--body-line-height: 1.5;

/* Captions */
--caption-size: 14px;
--caption-weight: 400;
--caption-contrast: high;      /* High contrast for readability */
```

### Layout & Spacing

#### Grid System
```css
/* 8px Grid Base Unit */
--grid-unit: 8px;

/* Spacing Scale */
--space-xs: 4px;               /* 0.5 * grid */
--space-sm: 8px;               /* 1 * grid */
--space-md: 16px;              /* 2 * grid */
--space-lg: 24px;              /* 3 * grid */
--space-xl: 32px;              /* 4 * grid */
--space-2xl: 40px;             /* 5 * grid */
--space-3xl: 48px;             /* 6 * grid */
--space-4xl: 64px;             /* 8 * grid */
```

#### Layout Principles
- **Consistent Padding**: Use grid multiples for all padding/margins
- **Generous White Space**: Minimum 24px between major sections
- **Logical Grouping**: Related data within frosted glass cards
- **Executive Readability**: Spacious layouts for easy scanning

### Components

#### Cards/Panels
```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;          /* Minimum radius */
  border-radius: 16px;          /* Maximum radius */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  padding: 24px;
}
```

#### Buttons
```css
.button-primary {
  /* Pill-shaped */
  border-radius: 24px;
  padding: 12px 24px;
  
  /* Subtle gradient fills */
  background: linear-gradient(135deg, #A4C8E7 0%, #C8E7D5 100%);
  
  /* Hover/focus animations */
  transition: all 0.2s ease;
}

.button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(164, 200, 231, 0.3);
}

.button-primary:focus {
  outline: 2px solid #A4C8E7;
  outline-offset: 2px;
}
```

#### Inputs
```css
.input-field {
  /* Rounded edges */
  border-radius: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  
  /* Soft inner shadow */
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  
  transition: all 0.2s ease;
}

.input-field:focus {
  /* Pastel glow on focus */
  border-color: #A4C8E7;
  box-shadow: 
    inset 0 1px 3px rgba(0, 0, 0, 0.05),
    0 0 0 3px rgba(164, 200, 231, 0.2);
  outline: none;
}
```

#### Charts
```css
/* Chart Configuration */
.chart-container {
  /* Pastel color fills */
  --chart-colors: #A4C8E7, #E7C8D2, #C8E7D5, #F5E6D3, #D2C8E7;
  
  /* Minimal lines */
  --grid-lines: rgba(0, 0, 0, 0.05);
  --axis-lines: rgba(0, 0, 0, 0.1);
  
  /* Refined tooltips */
  --tooltip-bg: rgba(255, 255, 255, 0.95);
  --tooltip-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

#### Tables
```css
.data-table {
  /* Zebra striping */
  tbody tr:nth-child(even) {
    background: rgba(247, 247, 247, 0.5);
  }
  
  /* Hover highlights */
  tbody tr:hover {
    background: rgba(164, 200, 231, 0.1);
    transition: background 0.2s ease;
  }
  
  /* Clear separation */
  border-collapse: separate;
  border-spacing: 0;
  
  th, td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }
}
```

### Animations & Microinteractions

#### Timing & Duration
```css
/* Animation Durations */
--duration-fast: 150ms;        /* < 200ms for microinteractions */
--duration-normal: 200ms;
--duration-slow: 300ms;

/* Easing Functions */
--ease-out: cubic-bezier(0.25, 0.46, 0.45, 0.94);
--ease-in-out: cubic-bezier(0.42, 0, 0.58, 1);
```

#### Animation Patterns
```css
/* Soft fade-ins */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Crossfades */
@keyframes crossfade {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

/* Gentle scaling */
@keyframes gentleScale {
  from { transform: scale(0.98); }
  to { transform: scale(1); }
}

/* Smooth hover effects */
.interactive-element {
  transition: all 0.15s ease-out;
}

.interactive-element:hover {
  transform: translateY(-1px);
  /* No distracting motion */
}
```

### Accessibility

#### WCAG 2.1 AA Compliance
```css
/* Contrast Ratios */
--min-contrast-normal: 4.5:1;  /* Normal text */
--min-contrast-large: 3:1;     /* Large text (18px+ or 14px+ bold) */

/* Focus Indicators */
*:focus-visible {
  outline: 2px solid #A4C8E7;
  outline-offset: 2px;
}

/* Touch Targets */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

#### Accessibility Features
- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Reader Support**: Proper ARIA labels and roles
- **Color Contrast**: All text meets WCAG AA standards
- **Focus Management**: Clear focus indicators and logical tab order
- **Motion Preferences**: Respect `prefers-reduced-motion`

## Implementation Examples

### Glass Card Component
```html
<div class="glass-card">
  <h2 class="card-heading">Monthly Spending</h2>
  <p class="card-body">Your spending insights for December 2024</p>
  <div class="card-actions">
    <button class="button-primary">View Details</button>
  </div>
</div>
```

### Form Input with Pastel Glow
```html
<div class="form-group">
  <label for="amount" class="form-label">Transaction Amount</label>
  <input 
    type="text" 
    id="amount" 
    class="input-field"
    placeholder="Enter amount in Rupiah"
  />
</div>
```

### Data Table with Hover Effects
```html
<table class="data-table">
  <thead>
    <tr>
      <th>Date</th>
      <th>Merchant</th>
      <th>Category</th>
      <th>Amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dec 15, 2024</td>
      <td>Starbucks</td>
      <td><span class="category-badge">Food & Drink</span></td>
      <td>Rp 75,000</td>
    </tr>
  </tbody>
</table>
```

## Responsive Design

### Breakpoints
```css
/* Mobile First Approach */
--mobile: 0px;                 /* Default */
--tablet: 768px;               /* iPad and up */
--desktop: 1024px;             /* Desktop and up */
--wide: 1440px;                /* Large screens */
```

### Mobile Adaptations
- **Increased Touch Targets**: 48px minimum on mobile
- **Simplified Layouts**: Single column on small screens
- **Reduced Animations**: Simpler transitions on mobile
- **Optimized Typography**: Slightly larger text on mobile

## Dark Mode Considerations

### Dark Mode Palette
```css
/* Dark Mode Base */
--dark-base: #1C1C1E;
--dark-elevated: #2C2C2E;

/* Dark Mode Panels */
--dark-panel: rgba(50, 50, 52, 0.7);

/* Dark Mode Accents */
--dark-accent-blue: #6BA3D8;
--dark-accent-pink: #D8A3B8;
--dark-accent-mint: #A3D8B9;
```

## Quality Checklist

### Visual Design
- [ ] Colors follow pastel palette guidelines
- [ ] Typography uses SF Pro fonts at specified sizes
- [ ] Spacing follows 8px grid system
- [ ] Components have glassmorphic styling

### Interaction Design
- [ ] Animations are under 200ms
- [ ] Hover states are subtle and smooth
- [ ] Focus states are clearly visible
- [ ] Touch targets meet 44px minimum

### Accessibility
- [ ] WCAG 2.1 AA contrast compliance
- [ ] Keyboard navigation works throughout
- [ ] Screen reader compatibility verified
- [ ] Motion preferences respected

---

*Last Updated: January 2025*
*Version: 1.0*
*Owner: Design Team*