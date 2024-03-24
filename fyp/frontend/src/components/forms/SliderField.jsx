import * as React from 'react';
import {Controller} from 'react-hook-form';
import Slider from '@mui/material/Slider';

export default function SliderField(props) {
    const {name, control, width, min, max, step, marks} = props
    return (
        <Controller
            name = {name}
            control = {control}
            defaultValue={1.00}
            render = {({
                field: {onChange, value},
                fieldState:{error},
                formState,
            }) => (
                <Slider
                    value={value}
                    valueLabelDisplay="auto"
                    min={min}
                    max={max}
                    step={step}
                    marks={marks}
                    sx={{width:{width}}}
                    onChange={onChange}
                    error = {!!error}
                    helperText = {error?.message}
                />
            )}
        />
    )
}