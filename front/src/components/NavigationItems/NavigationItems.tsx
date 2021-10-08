import React from 'react';
import ListItem from '@mui/material/ListItem';

import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import SendIcon from '@mui/icons-material/Send';
import BarChartIcon from '@mui/icons-material/BarChart';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import { useHistory } from 'react-router-dom';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import GroupIcon from '@mui/icons-material/Group';
import Divider from '@mui/material/Divider';
import useStyles from './NavigationItems.styles';

interface MainListItemsProps {
  handleCloseError: () => void;
}

export const MainListItems: React.FC<MainListItemsProps> = ({ handleCloseError }) => {
  const history = useHistory();
  const classes = useStyles();
  return (
    <div>
      <ListItem
        button
        onClick={() => {
          history.push('/dashboard');
          handleCloseError();
        }}>
        <ListItemIcon>
          <BarChartIcon />
        </ListItemIcon>
        <ListItemText primary="Статистика" />
      </ListItem>
      <ListItem
        button
        onClick={() => {
          history.push('/users');
          handleCloseError();
        }}>
        <ListItemIcon>
          <GroupIcon />
        </ListItemIcon>
        <ListItemText primary="Пользователи" />
      </ListItem>
      <Divider className={classes.root} />
      <ListItem
        button
        onClick={() => {
          history.push('/send');
          handleCloseError();
        }}>
        <ListItemIcon>
          <SendIcon />
        </ListItemIcon>
        <ListItemText primary="Написать Сообщение" />
      </ListItem>

      <ListItem
        button
        onClick={() => {
          history.push('/invite');
          handleCloseError();
        }}>
        <ListItemIcon>
          <PersonAddIcon />
        </ListItemIcon>
        <ListItemText primary="Пригласить" />
      </ListItem>
    </div>
  );
};

interface SecondaryListItemsProps {
  handleLogout: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

export const SecondaryListItems: React.FC<SecondaryListItemsProps> = ({ handleLogout }) => (
  <div>
    <ListItem onClick={handleLogout} component="button" button>
      <ListItemIcon>
        <ExitToAppIcon />
      </ListItemIcon>
      <ListItemText primary="Выйти" />
    </ListItem>
  </div>
);
