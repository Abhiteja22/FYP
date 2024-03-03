import '../App.css'
import { Box, Typography, Avatar, Button } from '@mui/material'
import MyTextField from './forms/MyTextField'
import {useForm} from 'react-hook-form';
import MyPasswordField from './forms/MyPasswordField';
import { Link, useNavigate } from 'react-router-dom';
import AxiosInstance from "./Axios";

const Register = () => {
    const navigate = useNavigate
    const {handleSubmit, control} = useForm()
    const submission = (data) => {
        console.log("Working")
        AxiosInstance.post(`register/`, {
            username: data.username,
            password: data.password,
        })
        .then(() => {
            navigate(`/`)
        })
        
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
                <Box className={"itemBox"}>
                    <Button variant='contained' type='submit' sx={{width: '100%', backgroundColor: '#0C0032'}}>
                        Register
                    </Button>
                </Box>
                <Box className={"itemBox"}>
                    <Button variant='contained' sx={{width: '100%', backgroundColor: '#0C0032'}} component={Link} to="/">
                        Registered? Log In
                    </Button>
                </Box>
            </Box>
            </form>
        </div>
    )
}

export default Register