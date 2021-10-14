import { CircularProgress } from '@mui/material/';
import React from 'react';
import useStyles from './PreloaderStyle';

interface PreloaderProps {
  children?: React.ReactNode;
}
const Preloader: React.FC<PreloaderProps> = () => {
  const classes = useStyles();

  return (
    <>
      <CircularProgress className={classes.preloader} />
    </>
  );
};
export default Preloader;
