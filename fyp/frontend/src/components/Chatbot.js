import React, { useState } from 'react';
// import { Container, Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { Button, Box, Typography, Container } from '@mui/material';
import MyTextField from './forms/MyTextField';

function Chatbot() {
//   const [message, setMessage] = useState('');
//   const [chat, setChat] = useState([]);

//   const sendMessage = async () => {
//     // send a POST request to the chatbot API with the user's message
//     const response = await axios.post('http://localhost:8000/chatbot/chatbot/', { message });

//     // update the chat state with the chatbot's response
//     setChat([...chat, { message, isUser: true }]);
//     setChat([...chat, { message: response.data.message, isUser: false }]);

//     // clear the message input field
//     setMessage('');
//   }

//   const [input, setInput] = useState([])
//   const [loading, setLoading] = useState(true)
//   const GetData = () => {
//     AxiosInstance.get(`chatbot/`).then((res) => {
//         setInput(res.data)
//         console.log(res.data)
//         setLoading(false)
//     })
//   }

//   useEffect(() => {
//     GetData();
//   },[])

//   const navigate = useNavigate()
//   const defaultValues = {
//     asset_ticker: 'AAPL',
//     quantity: 1,
//   }
//     const schema = yup
//     .object({
//         asset_ticker: yup.string().required('Asset ticker is a required field'),
//         quantity: yup.number().required('Quantity is a required field'),
//         portfolio: yup.string().required('Portfolio is a required field')
//     })
//     const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues, resolver: yupResolver(schema)})
//     const submission = (data) => {
//         AxiosInstance.post(`portfolioAsset/`, {
//             asset_ticker: data.asset_ticker,
//             quantity: data.quantity,
//             portfolio: data.portfolio,
//         })
//         .then((res) => {
//             navigate(`/`)
//         })
//     }

  return (
    <Container></Container>
//     <form onSubmit={handleSubmit(submission)}>
//     <Container>
//         <Typography sx={{marginLeft:'20px', color:'#fff'}}>
//             Chatbot
//         </Typography>
//         <Box className="chat">
//             {chat.map((chatMessage, index) => (
//                 <Box key={index} className={`message ${chatMessage.isUser ? 'user' : 'chatbot'}`}>
//                     {chatMessage.message}
//                 </Box>
//             ))}
//         </Box>
//         <Box>
//             <MyTextField
//                 label="Input"
//                 name="input"
//                 control={control}
//                 placeholder="Type your message here"
//                 width={'30%'}
//             />
//             <Button variant='contained' type='submit'>
//                 Send
//             </Button>
//         </Box>
//     </Container>
//     </form>
   );
}

export default Chatbot;