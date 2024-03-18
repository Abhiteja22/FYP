import PropTypes from 'prop-types';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

// ----------------------------------------------------------------------

export default function LargeWidget({ title, description, description2, icon, positive, color = 'primary', sx, height, ...other }) {
  return (
    <Card
      component={Stack}
      spacing={3}
      direction="row"
      sx={{
        px: 2,
        py: 5,
        borderRadius: 2,
        width: {},
        height: height ? height : 'auto',
        ...sx,
      }}
      {...other}
    >
      {icon && <Box sx={{ width: 64, height: 64 }}>{icon}</Box>}

      <Stack spacing={0.5}>
        <Typography variant="subtitle2" sx={{ color: 'text.disabled' }}>
            {title}
        </Typography>
        <Typography variant="h4" noWrap>{description ? description : "NA"}</Typography>
        <Typography variant="h5" noWrap sx={{
                        color: positive ? 'darkgreen' : 'red',
                      }}>{description2 ? description2 : "NA"}</Typography>
      </Stack>
    </Card>
  );
}

LargeWidget.propTypes = {
  color: PropTypes.string,
  icon: PropTypes.oneOfType([PropTypes.element, PropTypes.string]),
  sx: PropTypes.object,
  title: PropTypes.string,
  description: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  description2: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
  height: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
};