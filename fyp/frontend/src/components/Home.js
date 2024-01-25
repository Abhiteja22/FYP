
import {React, useEffect, useMemo, useState} from "react";
import AxiosInstance from "./Axios";
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';
import Dayjs from 'dayjs';
import { Box, IconButton } from "@mui/material";
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {Link} from 'react-router-dom'

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
        }
        ],
        [],
    );
    
    const table = useMaterialReactTable({
        columns,
        data: myData,
        enableRowActions: true,
        renderRowActions: ({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            <IconButton color="secondary" component={Link} to={`edit/${row.original.id}`}>
              <EditIcon />
            </IconButton>
            <IconButton color="error" component={Link} to={`delete/${row.original.id}`}>
              <DeleteIcon />
            </IconButton>
          </Box>
        )
    });
      
    return (
        <div>
            { loading ? <p>Loading data...</p> :
            <MaterialReactTable table={table} />
            }
        </div>
    )
}

export default Home