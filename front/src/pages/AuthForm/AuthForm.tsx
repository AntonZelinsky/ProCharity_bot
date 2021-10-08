// ts-ignore
import React, { useState } from 'react';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { Controller, useForm } from 'react-hook-form';
import { TextField, Button, Link, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import useStyles from './AuthForm.styles';
import StatusLabel from '../../components/StatusLabel/StatusLabel';
import { useAsync } from '../../hooks/useAsync';

const schema = yup.object().shape({
  email: yup.string().email('Такой e-mail не подойдет').required('Поле e-mail необходимо к заполнению'),
  password: yup.string().required('Поле пароль необходимо к заполнению').min(8, 'Минимальная длина пароля 8 символов'),
});

export interface LoginFormValues {
  email: string;
  password: string;
}
interface AuthFormI {
  onLogin: (data: LoginFormValues) => Promise<void>;
}

const AuthForm: React.FC<AuthFormI> = ({ onLogin }) => {
  const {
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<Pick<LoginFormValues, 'email' | 'password'>>({ resolver: yupResolver(schema), mode: 'onTouched' });

  const classes = useStyles();
  const { error, run, isError, setError, setData, isLoading } = useAsync({
    data: null,
    error: null,
  });

  const handleResetLabel = () => {
    if (isError) {
      setError(null);
      return;
    }
    setData(null);
  };
  const [isPasswordVisible, setPasswordVisible] = useState(false);
  const handleClickShowPassword = () => {
    setPasswordVisible(!isPasswordVisible);
  };

  const onSubmit = async (userData: LoginFormValues) => {
    run(onLogin(userData));
  };

  return <>
    <StatusLabel
      isStatusLabelOpen={error}
      statusMessage={error}
      isError={isError}
      handleCloseError={handleResetLabel}
    />
    <form className={classes.authForm} onSubmit={handleSubmit(onSubmit)}>
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

        <Controller
          name="password"
          control={control}
          defaultValue=""
          render={({ field }) => (
            <TextField
              variant="outlined"
              label="Пароль"
              error={Boolean(errors.password?.message)}
              helperText={errors.password?.message}
              className={classes.authFormInput}
              type={isPasswordVisible ? 'text' : 'password'}
              size="medium"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      size="large">
                      {isPasswordVisible ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              {...field}
            />
          )}
        />
      </fieldset>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <>
          <Link component={RouterLink} to="/reset_password">
            Забыли пароль?
          </Link>
          <Button className={classes.authFormButton} type="submit">
            Войти
          </Button>
        </>
      )}
    </form>
  </>;
};

export default AuthForm;
