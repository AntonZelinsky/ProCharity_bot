/* eslint-disable no-console */
import { yupResolver } from '@hookform/resolvers/yup';
import clsx from 'clsx';
import { Button, TextField, CircularProgress, Typography } from '@mui/material';
import * as yup from 'yup';
import { Options } from 'ky';
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import useStyles from '../AuthForm/AuthForm.styles';
import StatusLabel from '../../components/StatusLabel/StatusLabel';
import { useAsync } from '../../hooks/useAsync';
import useMainStyles from '../../App.styles';

interface InviteProps {
  children?: React.ReactNode;
  onSubmit: (data: InviteFormValues) => Promise<any>;
  isMenuOpen: boolean
}

const schema = yup.object().shape({
  email: yup.string().email('Такой e-mail не подойдет').required('Поле e-mail необходимо к заполнению'),
});

export interface InviteFormValues extends Options {
  email: string;
}

const Invite: React.FC<InviteProps> = ({ onSubmit, isMenuOpen }) => {
  const classes = useStyles();
    const mainClasses = useMainStyles();
  const { data, error, run, isError, setData, isLoading, setError } = useAsync({
    data: null,
    error: null,
    status: 'idle',
  });

  const statusMessage = isError ? (error as string) : ((data?.message ?? '') as string);

  const isStatusLabelOpen = Boolean(error) || Boolean(data?.message);
  const handleResetLabel = () => {
    if (isError) {
      setError(null);
      return;
    }
    setData(null);
  };

  const {
    handleSubmit,
    control,
    formState: { errors },
    reset,
  } = useForm<Pick<InviteFormValues, 'email'>>({ resolver: yupResolver(schema), mode: 'onTouched' });

  return (
    <main
      className={clsx(mainClasses.content, {
        [mainClasses.contentShift]: isMenuOpen,
      })}>
      <div className={classes.invite}>
        <StatusLabel
          isStatusLabelOpen={isStatusLabelOpen}
          statusMessage={statusMessage}
          isError={isError}
          handleCloseError={handleResetLabel}
        />
        <Typography align='center' variant="h4">Пригласить нового администратора</Typography>
        <form
          className={classes.authForm}
          onSubmit={handleSubmit((dataS, e) => {
            run(onSubmit(dataS));
            console.log(e?.target.reset());
            reset({ email: '' });
            e?.target.reset();
          })}>
          <fieldset className={classes.authFormInputContainer}>
            <Controller
              name="email"
              control={control}
              defaultValue=""
              render={({ field }) => (
                <TextField
                  label="E-mail"
                  error={Boolean(errors.email?.message)}
                  helperText={errors.email?.message}
                  className={classes.authFormInput}
                  size="medium"
                  variant="outlined"
                  {...field}
                />
              )}
            />
          </fieldset>
          {isLoading ? (
            <CircularProgress />
          ) : (
            <Button className={classes.authFormButton} type="submit">
              отправить
            </Button>
          )}
        </form>
      </div>
    </main>
  );
};

export default Invite;
