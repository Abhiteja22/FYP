
import {React, useEffect, useMemo, useState} from "react";
import Dayjs from 'dayjs';
import { Box, Typography, Button, Stack, Grid, Container } from "@mui/material";
import PortfolioFilters from "./portfolio_filters";
import PortfolioSort from "./portfolio_sort"
import PortfolioCard from "./portfolio_card";
import { useTable, useSortBy } from 'react-table';
import useAxios from '../../utils/useAxios';
import Create from "./Create";

const Portfolios = () => {
    const [portfolio, setPortfolios] = useState([])
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const GetData = async () => {
      try {
        const response = await api.get('/portfolio/');
        setPortfolios(response.data)
        setLoading(false)
      } catch (error) {
        console.log(error)
        setError(error.response?.data.detail || "An error occurred while fetching the portfolios.")
      }
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
        {
          accessor: 'portfolio_value',
          Header: 'Portfolio Value'
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
        data: portfolio,
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
      
    const [openCreate, setOpenCreate] = useState(false);

    const handleOpenCreate = () => {
      setOpenCreate(true);
    };

    const handleCloseCreate = () => {
      setOpenCreate(false);
    }
    return (
      <div>
        <Box>
        {error && <p style={{ color: 'red' }}>{error}</p>}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
              <Typography variant="h4" component="h2">
                  Your Collection of Portfolios
              </Typography>
              <Box>
              <Create
                openCreate={openCreate}
                onOpenCreate={handleOpenCreate}
                onCloseCreate={handleCloseCreate}
              />
              </Box>
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

            <Grid container spacing={2}>
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

export default Portfolios