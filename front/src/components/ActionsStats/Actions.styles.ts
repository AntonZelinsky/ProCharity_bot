import { Theme } from '@mui/material/styles';

import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme: Theme) => ({
  table: {},
  title: {
    padding: 5,
  },
  subtitle: {
    fontWeight:'bold'
  }
}));

export default useStyles;
