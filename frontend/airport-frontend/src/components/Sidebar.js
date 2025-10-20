import React from 'react';
import { Drawer, List, ListItem, ListItemButton, ListItemText, Toolbar, Typography } from '@mui/material';
import { NavLink } from 'react-router-dom';

const drawerWidth = 240;

const Sidebar = () => {
  const navItems = [
    { text: 'Airports', path: '/' },
    { text: 'Import', path: '/import' },
    { text: 'Logs', path: '/logs' },
    {text: 'Search Flight', path: '/flights_integration'}
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap>
          Painel de Controle
        </Typography>
      </Toolbar>
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={NavLink}
              to={item.path}
              style={({ isActive }) => ({
                backgroundColor: isActive ? '#1976d2' : 'transparent',
                color: isActive ? 'white' : 'inherit',
              })}
            >
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar;