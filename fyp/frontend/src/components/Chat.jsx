
import {React, useEffect, useMemo, useState} from "react";
import AxiosInstance from '../utils/Axios';
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';
import { Box, IconButton } from "@mui/material";
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {Link} from 'react-router-dom'
import ChatIcon from '@mui/icons-material/Chat';
import AddIcon from '@mui/icons-material/Add';
import useAxios from '../utils/useAxios';

const Chat = () => {
    const [myData, setMydata] = useState([])
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const GetData = async () => {
        const data = await api.get(`chatbot/chat/`)
        // AxiosInstance.get(`chatbot/chat/`, {headers: {'Content-Type': 'application/json', 'Authorization': 'token 0817b0aacc9a51627b9067e4d5b110c26caa20f6'}}).then((res) => {
        //     setMydata(res.data)
        //     console.log(res.data)
        //     setLoading(false)
        // })
        setMydata(data)
        console.log(data)
        setLoading(false)
    }

    useEffect(() => {
        GetData();
    },[])

    
    const columns = useMemo(
        () => [
        {
            accessorKey: 'name',
            header: 'Name',
            size: 150,
        }
        ],
        [],
    );
    const submission = (chatId) => {
        AxiosInstance.delete(`chatbot/chat/delete/${chatId}/`, {headers: {'Content-Type': 'application/json', 'Authorization': 'token 0817b0aacc9a51627b9067e4d5b110c26caa20f6'}})
        .then((res) => {
            setMydata(currentData => currentData.filter(chat => chat.id !== chatId));
        })
        .catch((error) => {
            console.error("Error deleting chat: ", error);
        });
    }
    
    const table = useMaterialReactTable({
        columns,
        data: myData,
        enableRowActions: true,
        renderRowActions: ({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            <IconButton color="secondary" component={Link} to={`${row.original.id}`}>
              <ChatIcon />
            </IconButton>
            <IconButton color="secondary" component={Link} to={`edit/${row.original.id}`}>
              <EditIcon />
            </IconButton>
            <IconButton color="error" onClick={() => submission(row.original.id)}>
              <DeleteIcon />
            </IconButton>
          </Box>
        )
    });
      
    return (
        <div>
            <Box>
                Create Chat
                <IconButton color="secondary" component={Link} to={`create`}>
                    <AddIcon />
                </IconButton>
            </Box>
            { loading ? <p>Loading data...</p> :
            <MaterialReactTable table={table} />
            }
        </div>
    )
}

export default Chat