import makeStyles from '@mui/styles/makeStyles';

const drawerWidth = 250;

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24,
  },
  date: {
    textAlign: 'right'
  },
  divider: {
    marginTop: 10,
    marginBottom: 10,
  },
  drawerPosition: {
    position: 'fixed',
    top: '0',
    left: '0',
    height: '100%',
    background: theme.palette.background.paper,
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    position: 'fixed',
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  paper: {
    padding: 20,
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
    gap: 30,
  },
  iconCross: {
    fill: theme.palette.error.main,
  },
  iconCheckMark: {
    fill: theme.palette.success.main,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    background: theme.palette.background.paper,
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperMobile: {
    marginTop: 65
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: {
    flexGrow: 1,
  },
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
    marginTop: 100,
    '& .quill': {
      width: '90%',
    },
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  richTextEditor: {
    maxWidth: '60%',
  },
  fixedHeight: {
    height: 240,
  },
  authFormTitle: {
    width: '100%',
    textAlign: 'center',
    fontSize: '2rem',
    lineHeight: '2rem',
  },
  headerContainer: {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    position: 'relative',
  },
  buttonThemeContainer: {
    paddingRight: 10,
    position: 'absolute',
    right: '0',
  },
  statusContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    minWidth: 180,
    gap: 20,
  },
}));

export default useStyles;
