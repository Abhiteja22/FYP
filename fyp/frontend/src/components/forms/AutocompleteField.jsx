import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import {Box, Autocomplete, TextField } from '@mui/material';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Chip from '@mui/material/Chip';
import {Controller} from 'react-hook-form';
import FormHelperText from '@mui/material/FormHelperText';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

export default function AutocompleteField(props) {
  const theme = useTheme();
  const {label, name, control, width, options} = props
  return (
            <Controller
            name = {name}
            control = {control}
            render = {({
                field: {onChange, value},
                fieldState:{error},
                formState,
            }) => (
                <Autocomplete
                id="country-select-demo"
                sx={{ width: {width} }}
                options={options}
                autoHighlight
                getOptionLabel={(option) => option.label}
                value={options.find(option => option.id === value) || null}
                onChange={(event, newValue) => {
                    onChange(newValue ? newValue.id : null);
                }}
                renderOption={(props, option) => (
                    <Box component="li" sx={{ '& > img': { mr: 2, flexShrink: 0 } }} {...props} key={option.id}>
                    {option.label} ({option.ticker})
                    </Box>
                )}
                renderInput={(params) => (
                    <TextField
                    {...params}
                    label={label}
                    inputProps={{
                        ...params.inputProps,
                        autoComplete: 'new-password', // disable autocomplete and autofill
                    }}
                    error = {!!error}
                    helperText = {error?.message}
                    />
                )}
                />
            )}
            />
        
  );
}