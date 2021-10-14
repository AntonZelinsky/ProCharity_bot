import React from 'react'
import { Badge } from '@mui/material';
import TelegramIcon from '@mui/icons-material/Telegram';
import useStyles from './BotStatus.styles';

interface BotStatusProps {
    status:boolean | undefined
}
const BotStatus: React.FC<BotStatusProps> = ({ status }) => {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Badge color={status ? 'secondary' : 'error'} variant="dot">
        <TelegramIcon />
      </Badge>
    </div>
  );
};

export default BotStatus
