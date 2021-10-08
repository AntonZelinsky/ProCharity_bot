import { Theme } from '@mui/material/styles';

import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme: Theme) => ({
  status: {
    position: 'absolute',
    inset: '75px 0 0 0 ',
    height: 'fit-content !important',
  },
  loggedOut: {
    inset: '60px 10% 0 10%',
  },
}));

export default useStyles;
