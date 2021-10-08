import makeStyles from '@mui/styles/makeStyles';


const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  title: {
    flexGrow: 1,
  },
  errorDate: {
        position: 'absolute',
    bottom: '-35px',
    color: 'red',
  },
  picker: {
    display: 'flex',
    gap: 20,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: '0.8rem'
  },

  errorDateHidden: {
    display: 'none',
    visibility: 'hidden'
  },
  pickerContainer: {
    display: 'flex',
    marginBottom: 30,
    gap: 30,
  },
  formContainer: {
    display: 'flex',
    marginTop: 'auto',
    gap: '20px',
    '& .MuiTextField-root': {},
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: 'black',
    },
    position: 'relative',
    alignItems: 'center',
  },
  button: {
    color: 'white',
    background: theme.palette.secondary.main,
    minHeight: 56,
  },
  content: {
    flexGrow: 1,
    height: '100%',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
    height: '100%',
  },
  fixedHeight: {
    minHeight: 240,
  },
}));

export default useStyles;
