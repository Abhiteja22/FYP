import React, { useState } from 'react';
import { Container, Form } from 'react-bootstrap';
import axios from 'axios';
import { Button, Box, Typography, Grid, Paper } from '@mui/material';
import MyTextField from './forms/MyTextField';
import SendIcon from "@mui/icons-material/Send";
import {useForm} from 'react-hook-form';

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [chat, setChat] = useState([]);

    const { handleSubmit, control, reset } = useForm()

    const sendMessage = async () => {
        // Send POST request to chatbot API with user's message
        const response = await axios.post('http://localhost:8000/chatbot/chatbot/', { message });

        // Update chat state
        setChat([...chat, { message, isUser: true }]);
        setChat([...chat, { message: response.data.message, isUser: false }]);

        // // Clear message input
        setMessage('');

        reset(); // Reset form fields handled by react-hook-form
        console.log(response)
    }

    return (
        <form onSubmit={handleSubmit(sendMessage)}>
        <Box sx={{height: '100vh', display: 'flex', flexDirection: 'column'}}>
            <Box sx={{flexGrow: 1, overflow: 'auto', p: 2}}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2}}>
                    <Paper variant='outlined' sx={{p: 1, backgroundColor: 'primary.light'}}>
                        <Typography variant="body1">Working</Typography>
                    </Paper>
                </Box>
            </Box>
            <Box sx={{p: 2, backgroundColor: 'background.default'}}>
                <Grid container spacing={2}>
                    <Grid item xs={10}>
                        <MyTextField
                            label="Input"
                            name="input"
                            control={control}
                            placeholder="Type a question"
                            width={'30%'}
                        />
                    </Grid>
                    <Grid item xs={2}>
                        <Button fullWidth size='large' color='primary' variant='contained' type='submit' endIcon={<SendIcon/>}>
                            Send
                        </Button>
                    </Grid>
                </Grid>
            </Box>
        </Box>
        </form>
    )
}

export default Chatbot;