import { Theme } from '@mui/material/styles';

import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme: Theme) => ({
  preloader: {
    position: 'absolute',
    inset: '0',
    margin: 'auto',
  },
}));

export default useStyles;
