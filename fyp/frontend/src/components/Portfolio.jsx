
import {React, useEffect, useMemo, useState} from "react";
import AxiosInstance from '../utils/Axios';
import Dayjs from 'dayjs';
import { Box, IconButton, Typography, Button, Stack, Grid, Container } from "@mui/material";
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {Link} from 'react-router-dom'
import PortfolioFilters from "./portfolio_components/portfolio_filters";
import PortfolioSort from "./portfolio_components/portfolio_sort"
import PortfolioCard from "./portfolio_components/portfolio_card";
import { useTable, useSortBy } from 'react-table';
import { useAuthStore } from "../store/auth";

const Portfolio = () => {
    const [myData, setMydata] = useState([])
    const [loading, setLoading] = useState(true)
    const GetData = () => {
        AxiosInstance.get(`portfolio/`).then((res) => {
            setMydata(res.data)
            console.log(res.data)
            setLoading(false)
        })
    }

    useEffect(() => {
        GetData();
    },[])

    const columns = useMemo(
        () => [
        {
            accessor: 'name', //access nested data with dot notation
            Header: 'Name'
        },
        {
            accessor: 'creation_date',
            Cell: ({ value }) => Dayjs(value).format('DD MMMM YYYY'),
            Header: 'Created On'
        },
        // Add the Actions column here, at the end
        {
            id: 'actions', // 'id' is used since this column doesn't directly access data
            Header: 'Actions',
            Cell: ({row}) => (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <IconButton color="secondary" component={Link} to={`edit/${row.original.id}`}>
                        <EditIcon />
                    </IconButton>
                    <IconButton color="error" component={Link} to={`delete/${row.original.id}`}>
                        <DeleteIcon />
                    </IconButton>
                </Box>
            )
        }
        ],
        [],
    );
    const [sortConfig, setSortConfig] = useState({ id: 'name', desc: false });

    // Update your useTable hook to account for the custom sortConfig
    const {
      rows,
      prepareRow,
      setSortBy,
    } = useTable({
        columns,
        data: myData,
        initialState: { sortBy: [sortConfig] }
      },
      useSortBy
    );
    
    const handleSortChange = (newSortConfig) => {
        setSortConfig(newSortConfig);
        setSortBy([newSortConfig]);
    };

    const [openFilter, setOpenFilter] = useState(false);

    const handleOpenFilter = () => {
      setOpenFilter(true);
    };

    const handleCloseFilter = () => {
      setOpenFilter(false);
    };
      
    return (
      <div>
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
              <Typography variant="h4" component="h2">
                  Your Collection of Portfolios
              </Typography>
              <Button variant="contained" component={Link} to="/create">
                  Create New Portfolio
              </Button>
          </Box>
          <Box sx={{ width: '80%', maxWidth: 800, mx: 'auto' }}>
              {/* <MaterialReactTable table={table} /> */}
          </Box>
          { loading ? <p>Loading data...</p> :
          <Container>
            <Stack
              direction="row"
              alignItems="center"
              flexWrap="wrap-reverse"
              justifyContent="flex-end"
              sx={{ mb: 5 }}
            >
              <Stack direction="row" spacing={1} flexShrink={0} sx={{ my: 1 }}>
                <PortfolioFilters
                  openFilter={openFilter}
                  onOpenFilter={handleOpenFilter}
                  onCloseFilter={handleCloseFilter}
                />
                <PortfolioSort onSortChange={handleSortChange}/>
              </Stack>
            </Stack>

            <Grid container spacing={3}>
            {rows.map(row => {
                  prepareRow(row);
                  return ( <Grid key={row.original.id} xs={12} sm={6} md={3}>
                            <PortfolioCard portfolio={row.original} />
                          </Grid>
                  );
              })}
            </Grid>
          </Container>
          }
      </Box>
      </div>
    )
}

export default Portfolio