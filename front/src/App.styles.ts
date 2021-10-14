import { useRouteMatch } from 'react-router-dom';
import { Theme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import { themeDark } from './App.theme';

const drawerWidth = 268;

const useMainStyles = makeStyles((theme: Theme) => {
  const match = useRouteMatch('/send')?.isExact ?? false;
  return {
    root: {
      background: theme.palette.mode === 'light' ? themeDark.palette?.background?.default : '#FFFFF',
    },
    formContent: {
      position: 'relative',
    },
    content: {
      position: 'relative',
      minHeight: '100vh',
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      overflow: 'visible',
      marginLeft: '120px',
      marginTop: '60px',
      display: 'flex',
      flexDirection: 'column',
      width: `calc(100% - 175px)`,
      '@media (max-width: 599px)': {
        width: '90%',
        marginLeft: 'auto',
        marginRight: 'auto'
      },
    },
    contentShift: {
      overflow: 'visible',
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      width: match ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${drawerWidth + 20}px)`,
      marginLeft: 270,
    },
  };
});

export default useMainStyles;
