import React from 'react';
import Typography from '@mui/material/Typography';
import useStyles from './Users.styles';

interface UsersProps {
  text: number;
  title: string;
  lastUpdate?:string;
}
const Users: React.FC<UsersProps> = ({ text, title, lastUpdate = '' }) => {
  const classes = useStyles();
  const lastUpdateDate = new Date(lastUpdate.replace(/-/g, '/'));
  const options: any = {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
  };
  return (
    <>
      <Typography component="p" variant="h4">
        {text}
      </Typography>
      <Typography component="p" variant="h6">
        {title}
      </Typography>
      {lastUpdate && (
        <div>
          <Typography variant="body1"className={classes.depositContext}>
            Последнее обновление заданий
          </Typography>
          <Typography variant="body1" className={classes.depositContext}>
            {new Intl.DateTimeFormat('ru-Ru', options).format(lastUpdateDate)}
          </Typography>
        </div>
      )}
      <div />
    </>
  );
};

export default Users;
