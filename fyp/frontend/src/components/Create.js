
import React from "react";
import { Box, Typography, Button } from "@mui/material";
import MyTextField from "./forms/MyTextField";
import {useForm} from 'react-hook-form';
import AxiosInstance from "./Axios";
import { useNavigate } from "react-router-dom";
import { yupResolver } from "@hookform/resolvers/yup"
import * as yup from "yup"

const Create = () => {
    const navigate = useNavigate()
    const defaultValues = {
        name: '',
    }
    const schema = yup
    .object({
        name: yup.string().required('Name is a required field'),
    })
    const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues, resolver: yupResolver(schema)})
    const submission = (data) => {
        AxiosInstance.post(`portfolio/`, {
            name: data.name,
        })
        .then((res) => {
            navigate(`/`)
        })
    }
    return (
        <div>
            <form onSubmit={handleSubmit(submission)}>
            <Box sx={{display:'flex', width:'100%', backgroundColor:'#00003f', marginBottom:'10px'}}>
                <Typography sx={{marginLeft:'20px', color:'#fff'}}>
                    Create Portfolio
                </Typography>
            </Box>

            <Box sx={{display:'flex', width:'100%', boxShadow:3, padding:4, flexDirection:'column'}}>
                <Box sx={{display:'flex', justifyContent:'space-around', marginBottom: '40px'}}>
                    <MyTextField
                      label="Name"
                      name="name"
                      control={control}
                      placeholder="Provide a Portfolio Name"
                      width={'30%'}
                    />
                </Box>
                <Box sx={{display:'flex', justifyContent:'space-around'}}>
                    <Box sx={{display:'flex', justifyContent:'space-around', width:'30%'}}>
                        <Button variant='contained' type='submit'>
                            Submit
                        </Button>
                    </Box>
                </Box>
            </Box>
            </form>
        </div>
    )
}

export default Create