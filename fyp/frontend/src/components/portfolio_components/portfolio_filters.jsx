import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Radio from '@mui/material/Radio';
import Button from '@mui/material/Button';
import Drawer from '@mui/material/Drawer';
import Rating from '@mui/material/Rating';
import Divider from '@mui/material/Divider';
import Checkbox from '@mui/material/Checkbox';
import FormGroup from '@mui/material/FormGroup';
import RadioGroup from '@mui/material/RadioGroup';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import FormControlLabel from '@mui/material/FormControlLabel';

import FilterListIcon from '@mui/icons-material/FilterList';
import CloseIcon from '@mui/icons-material/Close';
import ClearAllIcon from '@mui/icons-material/ClearAll';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';

// ----------------------------------------------------------------------

const VALUE_OPTIONS = [
  { value: 'below', label: 'Below $1000' },
  { value: 'between', label: 'Between $1000 - $5000' },
  { value: 'above', label: 'Above $5000' },
];

// ----------------------------------------------------------------------

export default function PortfolioFilters({ openFilter, onOpenFilter, onCloseFilter }) {

//   const handlePriceChange = (event) => {
//     onPriceFilterChange(event.target.value); // Call the parent handler
//   };

    const [radioValue, setRadioValue] = useState(null);

    const handleRadioChange = (event) => {
        setRadioValue(event.target.value);
    };

    const handleClearFilters = () => {
    // Reset radio button state
        setRadioValue(null);
    };

  const renderPrice = (
    <Stack spacing={1}>
      <Typography variant="subtitle2">Value</Typography>
        <RadioGroup onChange={handleRadioChange}> {/* onChange={handlePriceChange} */}
            {VALUE_OPTIONS.map((item) => (
            <FormControlLabel
                key={item.value}
                value={item.value}
                control={<Radio />}
                label={item.label}
            />
            ))}
        </RadioGroup>
    </Stack>
  );
  const theme = useTheme()

  return (
    <>
      <Button
        disableRipple
        color="inherit"
        endIcon={<FilterListIcon/>}
        onClick={onOpenFilter}
      >
        Filters&nbsp;
      </Button>

      <Drawer
        anchor="right"
        open={openFilter}
        onClose={onCloseFilter}
        PaperProps={{
          sx: { width: 280, border: 'none', overflow: 'hidden', zIndex: theme.zIndex.drawer + 3,top: '64px', },
        }}
      >
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ px: 1, py: 2 }}
        >
          <Typography variant="h6" sx={{ ml: 1 }}>
            Filters
          </Typography>
          <IconButton onClick={onCloseFilter}>
            <CloseIcon/>
          </IconButton>
        </Stack>

        <Divider />

        <Stack spacing={3} sx={{ p: 3 }}>
        {renderPrice}
        </Stack>

        <Box sx={{ p: 3 }}>
          <Button
            fullWidth
            size="large"
            type="submit"
            color="inherit"
            variant="outlined"
            startIcon={<ClearAllIcon/>}
            onClick={handleClearFilters}
          >
            Clear All
          </Button>
        </Box>
      </Drawer>
    </>
  );
}

PortfolioFilters.propTypes = {
  openFilter: PropTypes.bool,
  onOpenFilter: PropTypes.func,
  onCloseFilter: PropTypes.func,
};