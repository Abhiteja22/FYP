import PropTypes from 'prop-types';
import { useState } from 'react';
import Dayjs from 'dayjs';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import { CardActions, CardContent, useTheme, IconButton } from '@mui/material';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import {Link} from 'react-router-dom'
import numeral from 'numeral';
import Tooltip from '@mui/material/Tooltip';
import Edit from './Edit';
import Delete from './Delete';

// ----------------------------------------------------------------------

export default function PortfolioCard({ portfolio }) {
  const theme = useTheme();
  const [openEdit, setOpenEdit] = useState(false);

    const handleOpenEdit = () => {
      setOpenEdit(true);
    };

    const handleCloseEdit = () => {
      setOpenEdit(false);
    };
    const [openDelete, setOpenDelete] = useState(false);

    const handleOpenDelete = () => {
      setOpenDelete(true);
    };

    const handleCloseDelete = () => {
      setOpenDelete(false);
    };
  return (
    <Card sx={{ m: 2, backgroundColor: theme.palette.primary.dark, borderRadius: 4 }}>
        <CardContent>
            <Typography variant='h6' sx={{ pb: 1 }} noWrap>
                {portfolio.name}
            </Typography>
            <Typography variant='h4'>
                {numeral(portfolio.portfolio_value).format('$0,0.00')}
            </Typography>
            <Typography variant='h7'>
                {Dayjs(portfolio.creation_date).format('DD MMMM YYYY')}
            </Typography>
        </CardContent>
        <CardActions sx={{ justifyContent: 'center' }}>
            <Tooltip title="Edit">
                <Edit
                    openEdit={openEdit}
                    onOpenEdit={handleOpenEdit}
                    onCloseEdit={handleCloseEdit}
                    Id={portfolio.id}
                />
            </Tooltip>
            <Tooltip title="Delete">
                <Delete
                    openDelete={openDelete}
                    onOpenDelete={handleOpenDelete}
                    onCloseDelete={handleCloseDelete}
                    Id={portfolio.id}
                />
            </Tooltip>
            <Tooltip title="View">
                <IconButton color="info" component={Link} to={`/portfolios/${portfolio.id}`}>
                    <ShowChartIcon />
                </IconButton>
            </Tooltip>
        </CardActions>
    </Card>
  );
}

PortfolioCard.propTypes = {
  portfolio: PropTypes.object,
};