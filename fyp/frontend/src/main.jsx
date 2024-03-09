import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import {BrowserRouter as Router} from 'react-router-dom';
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material';

const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // Light mode palette
          background: {
            default: '#f5f5ff',
          },
          primary: {
            main: '#104ec1',
          },
          secondary: {
            main: '#8b98e9',
            light: '#a2aced'
          },
        }
      : {
          // Dark mode palette
          background: {
            default: '#00000e',
          },
          primary: {
            main: '#3e7cef',
          },
          secondary: {
            main: '#162374',
            dark: '#0f1851'
          },
        }),
  },
});

// Create a theme instance based on the preferred mode
const theme = createTheme(getDesignTokens('dark'));

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
  <CssBaseline />
    <Router>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </Router>
  </ThemeProvider>
);
