import { Theme } from '@mui/material/styles';

import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles((theme: Theme) => ({
  authForm: {
    display: 'flex',
    maxWidth: '314px',
    margin: '60px 0 0 0',
    flexDirection: 'column',
    border: 'none',
    padding: '0',
    width: '288px',
    gap: 20,
    alignItems: 'center',
  },

  authFormInputContainer: {
    position: 'relative',
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 35,
    width: '100%',
    border: 'none',
  },

  authFormSubmitContainer: {
    display: 'flex',
    justifyContent: 'center',
    position: 'relative',
    width: '100%',
  },
  authFormResetError: {
    display: 'grid',
    placeItems: 'center',
    gap: 30,
    width: '90%',
  },
  authFormButtonContainer: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
  },

  authFormButton: {
    cursor: 'pointer',
    width: '100%',
    color: 'white',
    maxWidth: '230px',
    minHeight: '44px',
    backgroundPosition: 'center',
    background: theme.palette.secondary.main,
    border: 'none',
    padding: '0',
  },

  authFormInput: {
    backgroundColor: theme.palette.background.paper,
    filter: 'none',
    borderColor: 'transparent',
    borderRadius: '4px',
    border: 'none',
    width: '100%',
    color: '#ffff',
    position: 'relative',

    '& input:-webkit-autofill': {
      '-webkit-box-shadow': `0 0 0px 1000px #4040 inset`,
      transitionDelay: '9999s',
    },
  },
}));

export default useStyles;
