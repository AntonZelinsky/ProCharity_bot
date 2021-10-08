import React, { useEffect, useRef, useState, Suspense } from 'react';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { Controller, useForm } from 'react-hook-form';
import { TextField, Button, Typography, Link, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import { useHistory, useParams, Link as RouterLink } from 'react-router-dom';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import ky, { Options } from 'ky';
import useStyles from './ResetForm.styles';
import { useAsync } from '../../hooks/useAsync';
import StatusLabel from '../../components/StatusLabel/StatusLabel';
import Preloader from '../../components/Preloader/Preloader';
import { apiUrl } from '../../App';

const schema = yup.object().shape({
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

export interface ResetFormValues extends Options {
  password: string;
  passwordConfirmation?: string;
}
interface ResetFormProps {
  onSubmit: (data: ResetFormValues, params: { id: string }) => Promise<void>;
}

const ResetForm: React.FC<ResetFormProps> = ({ onSubmit }) => {
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
  } = useForm<Pick<ResetFormValues, 'password' | 'passwordConfirmation'>>({
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
  const submitResetForm = (data: ResetFormValues) => {
    const newData = data
    delete newData?.passwordConfirmation;
    run(onSubmit(newData, params));
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
          <form className={classes.authForm} onSubmit={handleSubmit(submitResetForm)}>
            <fieldset className={classes.authFormInputContainer}>
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
        <div className={classes.authFormResetError}>
          <Typography variant="h4">{isSuccess ? 'Вы успешно зарегистрировались' : isInviteValid}</Typography>
          <Link component={RouterLink} to="/">
            Вернуться на главную
          </Link>
        </div>
      )}
    </Suspense>
  );
};

export default ResetForm;
