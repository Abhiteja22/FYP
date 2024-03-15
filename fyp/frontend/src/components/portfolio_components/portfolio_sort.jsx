import { useState } from 'react';

import Menu from '@mui/material/Menu';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import { listClasses } from '@mui/material/List';
import Typography from '@mui/material/Typography';

import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

// ----------------------------------------------------------------------

const SORT_OPTIONS = [
  { value: 'name', label: 'Name' },
//   { value: 'valueAsc', label: 'Value: Low-High' },
//   { value: 'valueDes', label: 'Value: High-Low' },
  { value: 'creation_date_Asc', label: 'Creation Date: Oldest-Newest' },
  { value: 'creation_date_Des', label: 'Creation Date: Newest-Oldest' },
  { value: 'portfolio_value_Asc', label: 'Portfolio Value: Lowest-Highest' },
  { value: 'portfolio_value_Des', label: 'Portfolio Value: Highest-Lowest' }
];

export default function PortfolioSort({ onSortChange }) {
  const [open, setOpen] = useState(null);
  const [selectedSort, setSelectedSort] = useState('name');

  const handleOpen = (event) => {
    setOpen(event.currentTarget);
  };

  const handleClose = () => {
    setOpen(null);
  };

  const handleSelect = (value) => {
    setSelectedSort(value); // Update local state with selected sort option
    handleClose(); // Close the menu
    if(onSortChange) {
        // Determine sort direction and any special logic based on the selection
        let sortConfig = { id: value, desc: false };
        if (value === 'creation_date_Asc') {
            // Assuming you want the oldest first; set desc to true if newest first
            sortConfig.id = 'creation_date'
            sortConfig.desc = false;
        } else if (value === 'creation_date_Des') {
            sortConfig.id = 'creation_date'
            sortConfig.desc = true;
        } else if (value === 'portfolio_value_Asc') {
          sortConfig.id = 'portfolio_value'
          sortConfig.desc = false;
        } else if (value === 'portfolio_value_Des') {
          sortConfig.id = 'portfolio_value'
          sortConfig.desc = true;
        }
        onSortChange(sortConfig);
    }
  };

  return (
    <>
      <Button
        disableRipple
        color="inherit"
        onClick={handleOpen}
        endIcon={open ? <ExpandLessIcon/> : <ExpandMoreIcon/>}
      >
        Sort By:&nbsp;
        <Typography component="span" variant="subtitle2" sx={{ color: 'text.secondary' }}>
            {SORT_OPTIONS.find(option => option.value === selectedSort)?.label}
        </Typography>
      </Button>

      <Menu
        open={!!open}
        anchorEl={open}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{
          paper: {
            sx: {
              [`& .${listClasses.root}`]: {
                p: 0,
              },
            },
          },
        }}
      >
        {SORT_OPTIONS.map((option) => (
          <MenuItem key={option.value} selected={option.value === selectedSort} onClick={() => handleSelect(option.value)}>
            {option.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}