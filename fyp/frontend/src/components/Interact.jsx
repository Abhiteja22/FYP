import { useParams } from 'react-router-dom';
import {React, useEffect, useState, useRef} from "react";
import AxiosInstance from '../utils/Axios';
import { Box, Container, Divider, Button, Paper, useTheme, Avatar, Typography, CssBaseline } from "@mui/material";
import {useForm} from 'react-hook-form';
import MyTextField from "./forms/MyTextField";
import CircularProgress from '@mui/material/CircularProgress';
import Markdown from 'react-markdown';

const Interact = () => {
    const { chatId } = useParams();
    const [myData, setMydata] = useState([])
    const [loading, setLoading] = useState(true)
    const [newLoading, setNewLoading] = useState(false)
    const [inputValue, setInputValue] = useState(''); // For the input field
    const bottomRef = useRef(null);
    const GetData = () => {
        AxiosInstance.get(`chatbot/chat/messages/${chatId}/`, {
            headers: {
                'Content-Type': 'application/json', 
                'Authorization': 'token 0817b0aacc9a51627b9067e4d5b110c26caa20f6'
            }
        }).then((res) => {
            setMydata(res.data)
            console.log(res.data)
            setLoading(false)
        }).catch((error) => {
            console.error("Error fetching data: ", error);
            setLoading(false);
        });
    }

    useEffect(() => {
        if(chatId) { // Only fetch data if chatId is available
            GetData();
        }
    },[chatId])
    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [myData]);

    const defaultValues = {
        input: '',
    }
    const {handleSubmit, control, reset} = useForm({defaultValues:defaultValues})
    const submission = (data) => {
        setNewLoading(true)
        console.log(data);
        AxiosInstance.post(`chatbot/chat/messages/${chatId}/`, {
            input: data.input,
        }, {
            headers: {
                'Content-Type': 'application/json', 
                'Authorization': 'token 0817b0aacc9a51627b9067e4d5b110c26caa20f6'
            }
        })
        .then((res) => {
            setMydata(prevMessages => [...prevMessages, res.data]);
            reset({ input: '' });
            console.log(res.data)
            setNewLoading(false)
        }).catch((error) => {
            console.error("Error fetching data: ", error);
            setNewLoading(false);
        });
    };
    const theme = useTheme();
    const backgroundColor = theme.palette.mode === 'dark' ? theme.palette.secondary.dark : theme.palette.secondary.light;
      
    return (
        <Container maxWidth="lg" sx={{ mt: 4, position: 'relative', height: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column', bgcolor: backgroundColor }}>
            <Paper elevation={3} sx={{ p: 2, overflow: 'auto', flexGrow: 1, mb: 2, bgcolor: 'transparent' }}>
                {loading ? <p>Loading data...</p> : myData.map((message, index) => (
                    <Box key={index} sx={{ '&:not(:last-child)': { mb: 2 } }} ref={index === myData.length - 1 ? bottomRef : null}>
                        <Box sx={{ color: 'white', p: 2, wordBreak: 'break-word' }}>
                            <Box sx={{ display: 'flex', mb: 1 }}>
                                <Avatar sx={{ mr: 1, width: 24, height: 24 }}>U</Avatar>
                                <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', fontWeight: 'bold', mr: 1 }}>Username</Typography>
                            </Box>
                            {message.input}
                        </Box>
                        <Divider sx={{ my: 1 }} />
                        <Box sx={{ color: 'white', p: 2, wordBreak: 'break-word' }}>
                            <Box sx={{ display: 'flex', mb: 1 }}>
                                <Avatar variant="square" alt="Riment" src="src/static/images/logo.png" sx={{ mr: 1, width: 24, height: 24 }} />
                                <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', fontWeight: 'bold', mr: 1 }}>Riment</Typography>
                            </Box>
                            <Markdown>
                                {message.output}
                            </Markdown>
                        </Box>
                        <Divider sx={{ my: 1 }} />
                    </Box>
                ))}
            </Paper>
            <Box component="form" noValidate onSubmit={handleSubmit(submission)} sx={{ display: 'flex', position: 'sticky', bottom: 0, pb: 2, pt: 1, bgcolor: backgroundColor }}>
                <MyTextField
                    name="input"
                    control={control}
                    label="Input"
                    placeholder="Type your message here"
                    width="80%"
                />
                <Button
                    type="submit"
                    variant="contained"
                    sx={{ width: '20%' }}
                    disabled={newLoading}
                >
                    {newLoading ? (
                        <CircularProgress size={24} color="inherit" />
                        ) : (
                            "Send"
                        )
                    }
                </Button>
            </Box>
        </Container>
    )
}

export default Interact