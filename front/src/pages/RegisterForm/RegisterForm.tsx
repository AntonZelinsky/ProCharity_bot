/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable no-unused-vars */
import React, { useEffect, useRef, useState, Suspense } from 'react';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { Controller, useForm } from 'react-hook-form';
import { TextField, Button, Typography, Link, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import { useHistory, useParams, Link as RouterLink } from 'react-router-dom';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import ky, { Options } from 'ky';
import useStyles from './RegisterForm.styles';
import { useAsync } from '../../hooks/useAsync';
import StatusLabel from '../../components/StatusLabel/StatusLabel';
import Preloader from '../../components/Preloader/Preloader';
import { apiUrl } from '../../App';

const schema = yup.object().shape({
  last_name: yup.string().required('Поле Имя необходимо к заполнению'),
  first_name: yup.string().required('Поле Фамилия необходимо к заполнению'),
  password: yup
    .string()
    .required('Поле пароль необходимо к заполнению')
    .min(8, 'Минимальная длина пароля 8 символов')
    .matches(/(?=.*\d)(?=.*[a-zа-я])(?=.*[A-ZА-Я])/g, 'Пароль должен содержать 1 цифру, 1 заглавную букву, 1 строчную'),
  passwordConfirmation: yup.string().oneOf([yup.ref('password'), null], 'Пароли должны совпадать'),
});

const paramsSchema = yup.object().shape({
  id: yup.string().uuid(),
});

export interface RegisterFormValues extends Options {
  first_name: string;
  last_name: string;
  password: string;
  passwordConfirmation?: string;
}
interface RegisterFormProps {
  onSubmit: (data: RegisterFormValues, params: { id: string }) => Promise<void>;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSubmit }) => {
  const history = useHistory();
  const password = useRef({});

  const params = useParams<{ id: string }>();
  const [isInviteValid, setInviteValid] = useState('');

  useEffect(() => {
    paramsSchema.validate(params).catch(() => history.push('/'));
    const handleTokenValidity = async () => {
      try {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const response = await ky.post(`${apiUrl}/auth/token_checker/`, {
          json: {
            token: params.id,
          },
          throwHttpErrors: false,
        });

        if (response.status !== 200) {
          const error = (await response.json()) as { message: string };
          throw new Error(error.message);
        }
      } catch (e) {
        const error = e as { message: string };
        setInviteValid(error.message);
      }
    };
    handleTokenValidity();
  }, [history, params]);

  const {
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<Pick<RegisterFormValues, 'first_name' | 'password' | 'last_name' | 'passwordConfirmation'>>({
    resolver: yupResolver(schema),
    mode: 'onTouched',
  });
  password.current = watch('password', '');
  const { error, run, isError, setError, setData, isLoading, isSuccess } = useAsync({
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
  const submitRegisterForm = (data: RegisterFormValues) => {
    run(onSubmit(data, params));
  };
  const [isPasswordVisible, setPasswordVisible] = useState(false);
  const handleClickShowPassword = () => {
    setPasswordVisible(!isPasswordVisible);
  };
  const classes = useStyles();

  return (
    <Suspense fallback={<Preloader />}>
      {!isInviteValid || isSuccess ? (
        <>
          <StatusLabel
            isStatusLabelOpen={error}
            statusMessage={error}
            isError={isError}
            handleCloseError={handleResetLabel}
          />
          <form className={classes.authForm} onSubmit={handleSubmit(submitRegisterForm)}>
            <fieldset className={classes.authFormInputContainer}>
              <Controller
                name="first_name"
                control={control}
                defaultValue=""
                render={({ field }) => (
                  <TextField
                    label="Имя"
                    fullWidth
                    error={Boolean(errors.first_name?.message)}
                    helperText={errors.first_name?.message}
                    className={classes.authFormInput}
                    size="medium"
                    variant="outlined"
                    {...field}
                  />
                )}
              />
              <Controller
                name="last_name"
                control={control}
                defaultValue=""
                render={({ field }) => (
                  <TextField
                    label="Фамилия"
                    error={Boolean(errors.last_name?.message)}
                    helperText={errors.last_name?.message}
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
              <Controller
                name="passwordConfirmation"
                control={control}
                defaultValue=""
                render={({ field }) => (
                  <TextField
                    variant="outlined"
                    label="Повторите пароль"
                    error={Boolean(errors.passwordConfirmation?.message)}
                    helperText={errors.passwordConfirmation?.message}
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
            <>
              {isLoading ? (
                <CircularProgress />
              ) : (
                <Button className={classes.authFormButton} type="submit">
                  Зарегистрироваться
                </Button>
              )}
            </>
          </form>
        </>
      ) : (
        <div className={classes.authFormRegisterError}>
          <Typography variant="h4">{isSuccess ? 'Вы успешно зарегистрировались' : isInviteValid}</Typography>
          <Link component={RouterLink} to="/">
            Вернуться на главную
          </Link>
        </div>
      )}
    </Suspense>
  );
};

export default RegisterForm;
