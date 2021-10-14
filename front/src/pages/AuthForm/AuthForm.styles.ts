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
  authFormError: {
    position: 'absolute',
    top: 70,
  },
  statusInfo: {
    position: 'absolute',
    top: 70,
  },
  invite: {
    display: 'grid',
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    width: '100%',
    placeItems: 'center',
    marginTop: 90,
  },
  authFormInputContainer: {
    position: 'relative',
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column',
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

  authFormButtonContainer: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
  },

  authFormButton: {
    cursor: 'pointer',
    width: '120px',
    minHeight: '44px',
    backgroundPosition: 'center',
    background: theme.palette.secondary.main,
    color: 'white',
    border: 'none',
    padding: '0',
  },

  authFormInput: {
    backgroundColor: theme.palette.secondary.dark,
    filter: 'none',
    borderRadius: '4px',
    color: theme.palette.text.primary,
    position: 'relative',
    width: '100%',
    maxWidth: '288px',
  },
}));

export default useStyles;
