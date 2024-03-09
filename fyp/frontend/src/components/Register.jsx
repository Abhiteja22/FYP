import '../App.css'
import { useState, useEffect } from 'react';
import { Box, Typography, Button } from '@mui/material'
import MyTextField from './forms/MyTextField'
import {useForm} from 'react-hook-form';
import MyPasswordField from './forms/MyPasswordField';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../utils/auth';
import { useAuthStore } from '../store/auth';
import AxiosInstance from '../utils/Axios';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const isLoggedIn = useAuthStore((state) => state.isLoggedIn);
    const navigate = useNavigate()

    useEffect(() => {
        if (isLoggedIn()) {
            navigate('/');
        }
    }, []);

    const resetForm = () => {
        setUsername('');
        setPassword('');
        setPassword2('');
    };

    const {handleSubmit, control} = useForm()
    const submission = async (data) => {
        const { error } = await register(data.username, data.email, data.first_name, data.last_name, data.password, data.password2);
        if (error) {
            alert(JSON.stringify(error));
        } else {
            navigate('/');
            resetForm();
        }
        console.log("Working")
    }
    return (
        <div className={"myBackground"}>
            <form onSubmit={handleSubmit(submission)}>
            <Box className={"whiteBox"}>
                <Box className={"itemBox"}>
                    <Typography variant="h5" noWrap component="div">
                        User Registration
                    </Typography>
                </Box>
                <Box className={"itemBox"}>
                    <MyTextField
                        label = "Username"
                        name = 'username'
                        width = {'100%'}
                        control={control}
                        placeholder="Provide a Username"
                    />
                </Box>
                <Box className={"itemBox"}>
                    <MyTextField
                        label = "First Name"
                        name = 'first_name'
                        width = {'100%'}
                        control={control}
                        placeholder="Provide a First Name"
                    />
                </Box>
                <Box className={"itemBox"}>
                    <MyTextField
                        label = "Last Name"
                        name = 'last_name'
                        width = {'100%'}
                        control={control}
                        placeholder="Provide a Last Name"
                    />
                </Box>
                <Box className={"itemBox"}>
                    <MyTextField
                        label = "Email Address"
                        name = 'email'
                        width = {'100%'}
                        control={control}
                        placeholder="Provide a Email Address"
                    />
                </Box>
                <Box className={"itemBox"}>
                    <MyPasswordField
                        label = "Password"
                        name = 'password'
                        width = {'100%'}
                        control={control}
                    />
                </Box>
                <Box className={"itemBox"}>
                    <MyPasswordField
                        label = "Confirm Password"
                        name = 'password2'
                        width = {'100%'}
                        control={control}
                    />
                </Box>
                <Box>
                    {password2 !== password ? 'Passwords do not match' : ''}
                </Box>
                <Box className={"itemBox"}>
                    <Button variant='contained' type='submit' sx={{width: '100%', backgroundColor: '#0C0032'}}>
                        Register
                    </Button>
                </Box>
                <Box className={"itemBox"}>
                    <Button variant='contained' sx={{width: '100%', backgroundColor: '#0C0032'}} component={Link} to="/login">
                        Registered? Log In
                    </Button>
                </Box>
            </Box>
            </form>
        </div>
    )
}

export default Register