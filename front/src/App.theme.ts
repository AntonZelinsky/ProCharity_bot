import { DeprecatedThemeOptions } from '@mui/material/styles';

export const themeLight: DeprecatedThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#3f51b5',
      dark: '#e3e3e3',
      light: '#C62FC6',
    },
    info: {
      main: '#AB81F1',
      light: '#1E0AB2',
    },
  },
}

export const themeDark: DeprecatedThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      main: '#44318d',
    },
    secondary: {
      main: '#AB81F1',
      dark: 'rgba(255,255,255,0.1)',
    },
    background: {
      default: '#06091F',
      paper: '#1F2235',
    },
    error: {
      main: '#F6483D',
    },
    divider: 'rgba(255,255,255,0.1)',
    info: {
      main: '#AB81F1',
      light: '#0AB242'
    },
    text: {
      primary: '#ffffff',
      secondary: '#676C7A',
      disabled: '#676C7A',
    },
  },
};
