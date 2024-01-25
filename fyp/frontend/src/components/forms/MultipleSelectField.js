import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
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

const names = [
  'Oliver Hansen',
  'Van Henry',
  'April Tucker',
  'Ralph Hubbard',
  'Omar Alexander',
  'Carlos Abbott',
  'Miriam Wagner',
  'Bradley Wilkerson',
  'Virginia Andrews',
  'Kelly Snyder',
];

function getStyles(name, personName, theme) {
  return {
    fontWeight:
      personName.indexOf(name) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  };
}

export default function MultipleSelectField(props) {
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
                <FormControl sx={{width:{width}}}>
                <InputLabel id="demo-multiple-chip-label">{label}</InputLabel>
                <Select
                labelId="demo-multiple-chip-label"
                id="demo-multiple-chip"
                multiple
                value={value}
                onChange={onChange}
                input={<OutlinedInput id="select-multiple-chip" label="Chip" />}
                renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                        <Chip key={value} label={value} />
                    ))}
                    </Box>
                )}
                error = {!!error}
                MenuProps={MenuProps}
                >
                {
                    options.map((option) => (
                        <MenuItem
                            key={option.id}
                            value={option.id}
                            >
                            {option.name}
                        </MenuItem>
                    ))
                }
                </Select>
                <FormHelperText sx={{color:"#d32f2f"}}> {error?.message} </FormHelperText>
                </FormControl>
            )}
            />
        
  );
}