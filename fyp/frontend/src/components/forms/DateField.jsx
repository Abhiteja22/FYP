import * as React from 'react';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import {Controller} from 'react-hook-form';

const isWeekend = (date) => {
    const day = date.day();
  
    return day === 0 || day === 6;
  };
export default function DateField(props) {
    const {label, control, name, minDate} = props
    
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Controller
        name = {name}
        control = {control}
        defaultValue=""
        render = {({
            field: {onChange, value},
            fieldState:{error},
        }) => (
            <DatePicker label={label} disableFuture minDate={minDate} onChange={onChange} value={value} shouldDisableDate={isWeekend}
          slotProps={{
            textField: {
                error: !!error,
                helperText: error?.message
            },
          }}/>
        )}
    />
    </LocalizationProvider>
  );
}
