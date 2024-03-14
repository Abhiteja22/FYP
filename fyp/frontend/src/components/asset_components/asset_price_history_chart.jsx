import PropTypes from 'prop-types';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';

// ----------------------------------------------------------------------

export default function AssetPriceHistory({ title, ...other }) {

  return (
    <Card {...other}>
      <CardHeader title={title} />

      <Box sx={{ p: 3, pb: 1, height: 425 }}>
        
      </Box>
    </Card>
  );
}

AssetPriceHistory.propTypes = {
  title: PropTypes.string,
};