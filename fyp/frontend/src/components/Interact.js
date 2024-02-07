import { useParams } from 'react-router-dom';
import {React, useEffect, useState, useRef} from "react";
import AxiosInstance from "./Axios";
import { Box, Container, Divider, Button, Paper } from "@mui/material";
import {useForm} from 'react-hook-form';
import MyTextField from "./forms/MyTextField";

const Interact = () => {
    const { chatId } = useParams();
    const [myData, setMydata] = useState([])
    const [loading, setLoading] = useState(true)
    const [inputValue, setInputValue] = useState(''); // For the input field
    const bottomRef = useRef(null);
    const GetData = () => {
        AxiosInstance.get(`chatbot/chat/${chatId}/`, {
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
        console.log(data);
        AxiosInstance.post(`chatbot/chat/${chatId}/`, {
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
            setLoading(false)
        }).catch((error) => {
            console.error("Error fetching data: ", error);
            setLoading(false);
        });
    };
      
    return (
        <Container maxWidth="md" sx={{ mt: 4, position: 'relative', height: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column' }}>
            <Paper elevation={3} sx={{ p: 2, overflow: 'auto', flexGrow: 1, mb: 2 }}>
                {loading ? <p>Loading data...</p> : myData.map((message, index) => (
                    <Box key={index} sx={{ '&:not(:last-child)': { mb: 2 } }} ref={index === myData.length - 1 ? bottomRef : null}>
                        <Box sx={{ bgcolor: 'purple', color: 'white', p: 2, wordBreak: 'break-word' }}>
                            {message.input}
                        </Box>
                        <Divider sx={{ my: 1 }} />
                        <Box sx={{ bgcolor: 'blue', color: 'white', p: 2, wordBreak: 'break-word' }}>
                            {message.output}
                        </Box>
                    </Box>
                ))}
            </Paper>
            <Box component="form" noValidate onSubmit={handleSubmit(submission)} sx={{ display: 'flex', position: 'sticky', bottom: 0, pb: 2, pt: 1, bgcolor: 'background.paper' }}>
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
                >
                    Send
                </Button>
            </Box>
        </Container>
    )
}

export default Interact