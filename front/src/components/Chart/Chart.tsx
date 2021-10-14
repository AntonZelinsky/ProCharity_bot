/* eslint-disable no-param-reassign */
/* eslint-disable no-return-assign */
import React from 'react';
import { Button } from '@mui/material';
import { ErrorBoundary } from 'react-error-boundary';
import { useTheme } from '@mui/material/styles';
import { LineChart, Line, XAxis, YAxis, Label, ResponsiveContainer, CartesianGrid, Tooltip } from 'recharts';
import { UserData } from '../../pages/Dashboard/Dashboard';
import useWindowSize, { Size } from '../../hooks/useWindowSize';

interface ChartProps {
  data: UserData | null;
  title: string;
}
interface ChartData {
  time: number;
  amountAdded?: number;
  amountUnsubscribed?: number;
  externalUsers?: number;
  allActive?: number;
  activeSubscribed?: number;
  activeUnsubscribed?: number;
}

export default function Chart({ data, title }: ChartProps) {
  const size: Size = useWindowSize();
  const { width } = size;

  const theme = useTheme();
  const chartData: ChartData[] = Object.keys(data?.all_users_statistic.added_external_users ?? {}).reduce(
    (previousValue, currentValue) => {
      const amountAdded = data?.all_users_statistic.added_users[currentValue] ?? 0;
      const day = Date.parse(currentValue);
      const amountUnsubscribed = data?.all_users_statistic.users_unsubscribed[currentValue] ?? 0;
      const externalUsers = data?.all_users_statistic.added_external_users[currentValue] ?? 0;

      const allActive = data?.active_users_statistic.all[currentValue] ?? 0;
      const activeSubscribed = data?.active_users_statistic.subscribed[currentValue] ?? 0;
      const activeUnsubscribed = data?.active_users_statistic.unsubscribed[currentValue] ?? 0;
      let newObject;
      if (title === 'Статистика пользователей за месяц') {
        newObject = { time: day, amountAdded, amountUnsubscribed, externalUsers };
      } else if (title === 'Статистика отписавшихся пользователей за месяц') {
        newObject = { time: day, amountUnsubscribed };
      } else if (title === 'Статистика активных пользователей за месяц') {
        newObject = { time: day, activeUnsubscribed, activeSubscribed, allActive };
      } else {
        newObject = { time: day, amountAdded, amountUnsubscribed };
      }
      previousValue.push(newObject);
      return previousValue;
    },
    [] as ChartData[],
  );

  const label = (value: any, name: any, props: any) => {
    let labelName;
    switch (name) {
      case 'amountAdded':
        labelName = 'Новых пользователей';
        break;
      case 'amountUnsubscribed':
        labelName = 'Отписавшихся пользователей';
        break;
      case 'externalUsers':
        labelName = 'Пользователей с сайта';
        break;
      case 'allActive':
        labelName = 'Активных пользователей';
        break;
      case 'activeSubscribed':
        labelName = 'Активных подписавшихся пользователей';
        break;
      case 'activeUnsubscribed':
        labelName = 'Активных отписавшихся пользователей';
        break;
      default:
        break;
    }
    return [value, labelName];
  };
  const tooltipText = (tooltipDate: any, payload: any) => {
    if (tooltipDate === 0 || tooltipDate === 'auto') {
      return 'date';
    }
    const db = new Date(tooltipDate);
    const options: any = { day: 'numeric', month: 'long', year: 'numeric' };
    const date = new Intl.DateTimeFormat('ru-Ru', options).format(db);
    return date;
  };

  const ErrorFallback = ({ error, resetErrorBoundary }: any) => (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <Button onClick={resetErrorBoundary}>Try again</Button>
    </div>
  );
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      {chartData.length && (
        <ResponsiveContainer height={400}>
          <LineChart
            data={chartData}
            margin={{
              top: 16,
              right: 16,
              bottom: 0,
              left: 24,
            }}>
            <CartesianGrid strokeDasharray="3 3" />

            {width && width > 1070 ? (
              <XAxis
                tickFormatter={(value, index: number) => {
                  const dateObj: Date = new Date(value);
                  const day = `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;
                  return day;
                }}
                interval={0}
                angle={30}
                dataKey="time"
                tickMargin={10}
                stroke={theme.palette.text.primary}
                style={{
                  fontSize: 'clamp(0.875rem, calc(0.875rem + ((1vw - 0.9rem) * 0.8929)), 0.5rem)',
                  minHeight: '0vw',
                }}
              />
            ) : (
              <XAxis
                tickFormatter={(value, index: number) => {
                  const dateObj: Date = new Date(value);
                  const day = `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;
                  return day;
                }}
                interval={1}
                angle={30}
                dataKey="time"
                tickMargin={10}
                stroke={theme.palette.text.primary}
                style={{
                  fontSize: 'clamp(0.875rem, calc(0.875rem + ((1vw - 0.9rem) * 0.8929)), 0.5rem)',
                  minHeight: '0vw',
                }}
              />
            )}
            <Tooltip
              label="дата"
              labelFormatter={tooltipText}
              formatter={label}
              wrapperStyle={{ width: 420, backgroundColor: '#FFF', color: 'black' }}
            />
        
            <YAxis allowDecimals={false} stroke={theme.palette.text.primary} yAxisId="left" orientation="left" />
            <YAxis allowDecimals={false} stroke={theme.palette.text.primary} yAxisId="right" orientation="right" />

            <Label angle={270} position="left" style={{ textAnchor: 'middle', fill: theme.palette.text.primary }}>
              Пользователи
            </Label>
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="amountAdded"
              stroke={theme.palette.secondary.light}
              dot={false}
            />

            <Line
              yAxisId="left"
              type="monotone"
              dataKey="amountUnsubscribed"
              stroke={theme.palette.error.main}
              dot={false}
            />



            <Line
              yAxisId="left"
              type="monotone"
              dataKey="externalUsers"
              stroke={theme.palette.info.light}
              dot={false}
            />

            <Line
              yAxisId="left"
              type="monotone"
              dataKey="activeSubscribed"
              stroke={theme.palette.secondary.light}
              dot={false}
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="activeUnsubscribed"
              stroke={theme.palette.error.main}
              dot={false}
            />

            <Line yAxisId="left" type="monotone" dataKey="allActive" stroke={theme.palette.info.light} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </ErrorBoundary>
  );
}
