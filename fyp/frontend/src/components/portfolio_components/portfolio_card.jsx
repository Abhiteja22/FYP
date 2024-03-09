import PropTypes from 'prop-types';

import Dayjs from 'dayjs';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { CardActions, CardContent, useTheme, IconButton } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {Link} from 'react-router-dom'

// ----------------------------------------------------------------------

export default function PortfolioCard({ portfolio }) {
  const theme = useTheme();
  return (
    <Card sx={{ m: 2, backgroundColor: theme.palette.primary.dark }}>
        <CardContent>
            <Typography variant='h6' sx={{ pb: 1 }}>
                {portfolio.name}
            </Typography>
            <Typography variant='h3'>
                $1000
            </Typography>
            <Typography variant='h7'>
                {Dayjs(portfolio.creation_date).format('DD MMMM YYYY')}
            </Typography>
        </CardContent>
        <CardActions>
            <IconButton color="secondary" component={Link} to={`edit/${portfolio.id}`}>
                <EditIcon />
            </IconButton>
            <IconButton color="error" component={Link} to={`delete/${portfolio.id}`}>
                <DeleteIcon />
            </IconButton>
        </CardActions>
    </Card>
  );
}

PortfolioCard.propTypes = {
  portfolio: PropTypes.object,
};