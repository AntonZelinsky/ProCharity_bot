import { TableContainer, TableHead, Table, TableRow, TableCell, TableBody } from '@mui/material';
import React from 'react';
import clsx from 'clsx';
import TablePagination from '@mui/material/TablePagination';
import Typography from '@mui/material/Typography';
import CheckIcon from '@mui/icons-material/Check';
import ClearIcon from '@mui/icons-material/Clear';
import { UsersTableData } from '../Dashboard/Dashboard';
import Preloader from '../../components/Preloader/Preloader';
import StatusLabel from '../../components/StatusLabel/StatusLabel';
import { useAsync } from '../../hooks/useAsync';
import useLocalStorage from '../../hooks/useLocalStorage';
import useStyles from './Users.styles';
import useMainStyles from '../../App.styles';

interface UsersProps {
  isMenuOpen: boolean
  fetchUserData: (limit: number, page: number) => Promise<UsersTableData>;
}

export const formatData = (date: string) => {
  const options: any = { day: 'numeric', month: 'long', year: 'numeric' };
  const dateIso = new Date(date);
  const dateLocalized = new Intl.DateTimeFormat('ru-Ru', options).format(dateIso);
  return dateLocalized;
};
const columns = ['ФИО', 'E-mail', 'Рассылка', 'Бот заблокирован', 'Имя пользователя', 'Дата Регистрации'];

const Users: React.FC<UsersProps> = ({ fetchUserData, isMenuOpen }) => {
  const classes = useStyles();
    const mainClasses = useMainStyles();
  const { data, error, isLoading, run, isError, reset } = useAsync({ status: 'idle', data: null, error: null });
  const [rowsPerPage, setRowsPerPage] = useLocalStorage<number>('rowsPerPage', 20);
  const [page, setPage] = useLocalStorage<number>('page', 1);
  const handleChangePage = (event: unknown, newPage: number) => {
    run(fetchUserData(newPage + 1, rowsPerPage));
    setPage(newPage + 1);
  };
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(+event.target.value);
    run(fetchUserData(1, +event.target.value));
    setPage(1);
  };
  React.useEffect(() => {
    run(fetchUserData(page, rowsPerPage));
  }, []);

  return <>
    {isLoading ? (
      <Preloader />
    ) : (
      <main
      className={clsx(mainClasses.content, {
        [mainClasses.contentShift]: isMenuOpen,
      })}>
        <StatusLabel isError={isError} isStatusLabelOpen={isError} statusMessage={error} handleCloseError={reset} />

        <section className={classes.section}>
          <Typography className={classes.title} variant="h5">
            Пользователи
          </Typography>
          <TableContainer className={classes.root}>
            <Table stickyHeader aria-label="sticky table">
              <TableHead>
                <TableRow>
                  {columns.map((column) => (
                    <TableCell key={column} align="left">
                      <Typography className={classes.subtitle} variant="subtitle1">
                        {column}
                      </Typography>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.result.map((result: any) => (
                  <TableRow key={result.telegram_id}>
                    <TableCell align="left">
                      <Typography variant="subtitle1">{`${result.first_name ?? 'Не указан'} ${
                        result.last_name ?? ''
                      }`}</Typography>
                    </TableCell>
                    <TableCell align="left">
                      <Typography variant="subtitle1">{result.email ?? 'Не указан'}</Typography>
                    </TableCell>
                    <TableCell align="left">
                      <div className={classes.container}>
                        {result.has_mailing ? (
                          <CheckIcon fontSize="small" className={classes.iconCheckMark} />
                        ) : (
                          <ClearIcon fontSize="small" className={classes.iconCross} />
                        )}
                      </div>
                    </TableCell>
                    <TableCell align="left">
                      <div className={classes.container}>
                        {result.banned ? (
                          <CheckIcon fontSize="small" className={classes.iconCheckMark} />
                        ) : (
                          <ClearIcon fontSize="small" className={classes.iconCross} />
                        )}
                      </div>
                    </TableCell>
                    <TableCell align="left">
                      <Typography variant="subtitle1">{result.username ?? 'Не указан'}</Typography>
                    </TableCell>
                    <TableCell align="left">
                      <Typography variant="subtitle1">{formatData(result.date_registration)}</Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <TablePagination
              component="div"
              rowsPerPageOptions={[20, 50, 100]}
              count={data?.total - 1 ?? 0}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              page={page - 1 ?? 0}
              rowsPerPage={rowsPerPage}
            />
          </TableContainer>
        </section>
      </main>
    )}
  </>;
};
export default Users;
