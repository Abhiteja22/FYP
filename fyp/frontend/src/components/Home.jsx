
import {React, useEffect, useMemo, useState} from "react";
import AxiosInstance from "./Axios";
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';
import Dayjs from 'dayjs';
import { Box, IconButton, Typography, Button } from "@mui/material";
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {Link} from 'react-router-dom'

import { darken, lighten, useTheme } from '@mui/material';

const Home = () => {
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
            accessorKey: 'name', //access nested data with dot notation
            header: 'Name',
            size: 150,
        },
        {
            accessorFn: (row) => Dayjs(row.creation_date).format('DD-MM-YYYY'),
            header: 'Created On',
            size: 150,
        },
        // Add the Actions column here, at the end
        {
            id: 'actions', // 'id' is used since this column doesn't directly access data
            header: 'Actions',
            Cell: ({row}) => (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <IconButton color="secondary" component={Link} to={`edit/${row.original.id}`}>
                        <EditIcon />
                    </IconButton>
                    <IconButton color="error" component={Link} to={`delete/${row.original.id}`}>
                        <DeleteIcon />
                    </IconButton>
                </Box>
            ),
            size: 100, // Adjust the size as needed
        }
        ],
        [],
    );

    const baseBackgroundColor = 'rgba(3, 44, 43, 1)'
    // theme.palette.mode === 'dark'
    //   ? 'rgba(3, 44, 43, 1)'
    //   : 'rgba(244, 255, 233, 1)';
    
    const theme = useTheme();
    const table = useMaterialReactTable({
        columns,
        data: myData,
        muiTablePaperProps: {
            elevation: 20,
            sx: {
              borderRadius: '20px',
            },
        },
        muiTableHeadCellProps: {
            sx: {
              fontWeight: 'bold',
              fontSize: '18px',
              backgroundColor: theme.palette.primary.dark // '#0C0032'
            },
        },
        muiTableBodyCellProps: {
            sx: {
              fontSize: '18px',
            },
        },
        muiTableBodyProps: {
            sx: {
              '& tr:nth-of-type(odd) > td':
                {
                  backgroundColor: theme.palette.primary.main//'#240090',
                },
              '& tr:nth-of-type(odd):hover > td':
                {
                  backgroundColor: lighten(theme.palette.primary.main, 0.2),
                },
              '& tr:nth-of-type(even) > td':
                {
                  backgroundColor: theme.palette.secondary.main//'#190061',
                },
              '& tr:nth-of-type(even):hover > td':
                {
                  backgroundColor: lighten(theme.palette.secondary.main, 0.2),
                },
            }
        },
        mrtTheme: (theme) => ({
            baseBackgroundColor: theme.palette.background.default //'#3500D3'
          }
        ),
    });
      
    return (
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
                { loading ? <p>Loading data...</p> :
                <MaterialReactTable table={table} />
                }
            </Box> 
        </Box>
    )
}

export default Home