import React from 'react';
import { Collapse, IconButton, Alert } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import clsx from 'clsx';
import { useRouteMatch } from 'react-router-dom';
import useStyles from './StatusLabel.style';

interface StatusLabelProps {
  isStatusLabelOpen: boolean;
  isError: boolean;
  handleCloseError: () => void;
  statusMessage: null | string;
}

const StatusLabel: React.FC<StatusLabelProps> = ({ isStatusLabelOpen, handleCloseError, isError, statusMessage }) => {
  const classes = useStyles();
  const matchLogin = useRouteMatch('/')?.isExact ?? false;

  const matchRegister = useRouteMatch('/register/:id')?.isExact ?? false;
  const matchReset = useRouteMatch('/reset_password')?.isExact ?? false;
  
  return (
    <Collapse
      in={isStatusLabelOpen}
      className={clsx(classes.status, (matchLogin || matchRegister || matchReset) && classes.loggedOut)}>
      <Alert
        severity={isError ? 'error' : 'success'}
        variant="outlined"
        action={
          <IconButton aria-label="close" color="inherit" size="small" onClick={handleCloseError}>
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }>
        {statusMessage}
      </Alert>
    </Collapse>
  );
};

export default StatusLabel;
