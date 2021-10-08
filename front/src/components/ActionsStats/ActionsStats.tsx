import React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

import Typography from '@mui/material/Typography';
import useStyles from './Actions.styles';

interface ActionsProps {
  actionsStats: { [key: string]: number } | undefined;
  title: string;
  cardTitle: string;
}
const Actions: React.FC<ActionsProps> = ({ actionsStats, title, cardTitle }) => {
  const classes = useStyles();
  const stats = actionsStats ?? { command_stats: 0 };
  return (
    <>
      <Typography className={classes.title} variant="h5">
        {cardTitle}
      </Typography>
      <Table className={classes.table} size="small">
        <TableHead>
          <TableRow>
            <TableCell>
              <Typography className={classes.subtitle} variant="h6">
                {title}
              </Typography>
            </TableCell>
            <TableCell align="right">
              <Typography className={classes.subtitle} variant="h6">
                Количество
              </Typography>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.keys(stats).map((actionName) => (
            <TableRow key={actionName}>
              <TableCell>
                <Typography variant="body1">{actionName}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="body1">{stats[actionName]}</Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
};

export default Actions;
