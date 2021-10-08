import { Theme } from '@mui/material/styles';

import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  section: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  title: {
    padding: 5,
  },
  subtitle: {
    fontWeight: 'bold',
  },
  iconCross: {
    fill: theme.palette.error.main,
  },
  iconCheckMark: {
    fill: theme.palette.success.main,
  },
  container: {
    alignItems: 'center',
    display: 'flex',
    width: '95%',
    justifyContent: 'space-between',
  },
}));

export default useStyles;
