import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Fade,
  Stack,
  alpha,
  useTheme,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Store as StoreIcon,
  Shield as ShieldIcon,
  Description as DescriptionIcon,
  Key as KeyIcon,
  History as HistoryIcon,
  School as SchoolIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Apps as AppsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { appleColors, appleBorderRadius, appleShadows } from '../theme/appleTheme';
import BrandLogo from '../components/BrandLogo';

const drawerWidth = 280;
const collapsedDrawerWidth = 80;

interface NavItem {
  title: string;
  path: string;
  icon: React.ReactElement;
  badge?: number;
}

const navItems: NavItem[] = [
  { title: 'Playground', path: '/playground', icon: <AutoAwesomeIcon /> },
  { title: 'Merchants', path: '/merchants', icon: <StoreIcon /> },
  { title: 'Guardrails', path: '/guardrails', icon: <ShieldIcon /> },
  { title: 'Prompt Templates', path: '/prompts', icon: <DescriptionIcon /> },
  { title: 'API Keys', path: '/api-keys', icon: <KeyIcon /> },
  { title: 'Search History', path: '/history', icon: <HistoryIcon /> },
  { title: 'Global Knowledge', path: '/knowledge', icon: <SchoolIcon /> },
];

const DashboardLayoutApple: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [drawerOpen, setDrawerOpen] = useState(true);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleProfileMenuClose();
    logout();
    navigate('/auth/login');
  };

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <Box sx={{ display: 'flex', bgcolor: appleColors.neutral[50], minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: alpha('#FFFFFF', 0.8),
          backdropFilter: appleColors.blur.medium,
          borderBottom: `1px solid ${appleColors.neutral[200]}`,
          transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="toggle drawer"
            onClick={toggleDrawer}
            sx={{
              mr: 2,
              color: appleColors.neutral[700],
              '&:hover': {
                backgroundColor: alpha(appleColors.primary.main, 0.08),
              },
            }}
          >
            {drawerOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>

          <BrandLogo size="small" showByBNI={true} />

          <Box sx={{ flexGrow: 1 }} />

          {/* Right side actions */}
          <Stack direction="row" spacing={1}>
            <IconButton
              sx={{
                color: appleColors.neutral[600],
                '&:hover': {
                  backgroundColor: alpha(appleColors.primary.main, 0.08),
                },
              }}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>

            <IconButton
              sx={{
                color: appleColors.neutral[600],
                '&:hover': {
                  backgroundColor: alpha(appleColors.primary.main, 0.08),
                },
              }}
            >
              <AppsIcon />
            </IconButton>

            <IconButton
              onClick={handleProfileMenuOpen}
              sx={{
                ml: 1,
                p: 0.5,
              }}
            >
              <Avatar
                sx={{
                  width: 36,
                  height: 36,
                  background: `linear-gradient(135deg, ${appleColors.accent.purple} 0%, ${appleColors.accent.pink} 100%)`,
                  fontSize: '0.875rem',
                  fontWeight: 600,
                }}
              >
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        PaperProps={{
          sx: {
            mt: 1.5,
            borderRadius: `${appleBorderRadius.lg}px`,
            boxShadow: appleShadows.xl,
            border: `1px solid ${appleColors.neutral[200]}`,
            minWidth: 220,
            background: alpha('#FFFFFF', 0.95),
            backdropFilter: appleColors.blur.light,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ px: 2, py: 1.5 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            {user?.email}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Administrator
          </Typography>
        </Box>
        <Divider sx={{ borderColor: appleColors.neutral[200] }} />
        <MenuItem
          onClick={handleProfileMenuClose}
          sx={{
            py: 1.5,
            '&:hover': {
              backgroundColor: alpha(appleColors.primary.main, 0.08),
            },
          }}
        >
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <MenuItem
          onClick={handleLogout}
          sx={{
            py: 1.5,
            color: appleColors.semantic.error,
            '&:hover': {
              backgroundColor: alpha(appleColors.semantic.error, 0.08),
            },
          }}
        >
          <ListItemIcon>
            <LogoutIcon fontSize="small" sx={{ color: appleColors.semantic.error }} />
          </ListItemIcon>
          Sign Out
        </MenuItem>
      </Menu>

      {/* Sidebar Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerOpen ? drawerWidth : collapsedDrawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerOpen ? drawerWidth : collapsedDrawerWidth,
            boxSizing: 'border-box',
            borderRight: `1px solid ${appleColors.neutral[200]}`,
            background: alpha(appleColors.neutral[50], 0.95),
            backdropFilter: appleColors.blur.light,
            transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <List sx={{ px: drawerOpen ? 2 : 1 }}>
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    sx={{
                      borderRadius: `${appleBorderRadius.md}px`,
                      transition: 'all 0.2s ease',
                      backgroundColor: isActive
                        ? alpha(appleColors.primary.main, 0.1)
                        : 'transparent',
                      '&:hover': {
                        backgroundColor: isActive
                          ? alpha(appleColors.primary.main, 0.15)
                          : alpha(appleColors.neutral[200], 0.5),
                      },
                      justifyContent: drawerOpen ? 'initial' : 'center',
                      px: drawerOpen ? 2 : 1,
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        mr: drawerOpen ? 2 : 'auto',
                        justifyContent: 'center',
                        color: isActive ? appleColors.primary.main : appleColors.neutral[600],
                      }}
                    >
                      {item.badge ? (
                        <Badge badgeContent={item.badge} color="error">
                          {item.icon}
                        </Badge>
                      ) : (
                        item.icon
                      )}
                    </ListItemIcon>
                    {drawerOpen && (
                      <ListItemText
                        primary={item.title}
                        primaryTypographyProps={{
                          fontSize: '0.9375rem',
                          fontWeight: isActive ? 600 : 500,
                          color: isActive ? appleColors.primary.main : appleColors.neutral[800],
                        }}
                      />
                    )}
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        }}
      >
        <Fade in={true} timeout={600}>
          <Box>
            <Outlet />
          </Box>
        </Fade>
      </Box>
    </Box>
  );
};

export default DashboardLayoutApple;