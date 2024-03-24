import PropTypes from 'prop-types';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Markdown from 'react-markdown';

// ----------------------------------------------------------------------

export default function AIResponse({ title, description, icon, color = 'primary', sx, height, ...other }) {
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
        <Markdown>{description ? description : "NA"}</Markdown>
      </Stack>
    </Card>
  );
}

AIResponse.propTypes = {
  color: PropTypes.string,
  icon: PropTypes.oneOfType([PropTypes.element, PropTypes.string]),
  sx: PropTypes.object,
  title: PropTypes.string,
  description: PropTypes.string,
  height: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]),
};