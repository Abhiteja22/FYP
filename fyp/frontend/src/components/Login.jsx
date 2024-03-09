import '../App.css'
import { Box, Typography, Avatar, Button } from '@mui/material'
import MyTextField from './forms/MyTextField'
import {useForm} from 'react-hook-form';
import MyPasswordField from './forms/MyPasswordField';
import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/auth';
import { login } from '../utils/auth'

const Login = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

    useEffect(() => {
        if (isLoggedIn()) {
            navigate('/');
        }
    }, []);

    const resetForm = () => {
        setUsername('');
        setPassword('');
    }

    const {handleSubmit, control} = useForm()
    const submission = async (data) => {
        const { error } = await login(data.username, data.password);
        if (error) {
            alert(error)
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
                    <Avatar variant="square" alt="Riment" src="src/static/images/logo.png" sx={{ marginRight: 1 }} />
                    <Typography variant="h5" noWrap component="div">
                        Riment
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
                    <MyPasswordField
                        label = "Password"
                        name = 'password'
                        width = {'100%'}
                        control={control}
                    />
                </Box>
                <Box className={"itemBox"}>
                    <Button variant='contained' type='submit' sx={{width: '100%', backgroundColor: '#0C0032'}}>
                        Log in
                    </Button>
                </Box>
                <Box className={"itemBox"}>
                    <Button variant='contained' sx={{width: '100%', backgroundColor: '#0C0032'}} component={Link} to="/register">
                        Register
                    </Button>
                </Box>
            </Box>
            </form>
        </div>
    )
}

export default Login