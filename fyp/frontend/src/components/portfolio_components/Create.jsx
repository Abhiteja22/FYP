
import {React, useState} from "react";
import { Box, Typography, Button, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import MyTextField from "../forms/MyTextField";
import SliderField from "../forms/SliderField";
import BasicSelectField from "../forms/BasicSelectField";
import {useForm} from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup"
import useAxios from '../../utils/useAxios';
import * as yup from "yup"
import { marks, options, timeOptions, defaultValues } from "./portfolio_constants";


export default function Create({ openCreate, onOpenCreate, onCloseCreate }) {
    const [error, setError] = useState('')
    const api = useAxios();
    const schema = yup
    .object({
        name: yup.string().required('Name is a required field'),
        risk_aversion: yup.number().required('Risk Aversion is a required field'),
        market_index: yup.string().required('Sector is a required field'),
        investment_time_period: yup.string().required('Time Period is a required field'),
        sector: yup.string().required('Sector is required')
    })
    const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues, resolver: yupResolver(schema)})
    const submission = async (data) => {
        try {
            // Find the option object that matches the submitted market_index value
            const selectedOption = options.find(option => option.value === data.market_index);
        
            // Extract the label from the selected option. If no option is found, default to an empty string or a placeholder value
            const sectorLabel = selectedOption ? selectedOption.label : '';
            const response = await api.post(`portfolio/`, {
                name: data.name,
                risk_aversion: data.risk_aversion,
                market_index: data.market_index,
                investment_time_period: data.investment_time_period,
                sector: sectorLabel
            })
            onCloseCreate()
            window.location.reload();
        } catch (error) {
            setError(error.response?.data.detail || "An error occurred while saving the portfolio.")
            onCloseCreate()
        }
    }
    return (
        <>
            <Button variant="contained" onClick={onOpenCreate}>
                  Create New Portfolio
            </Button>
            <form onSubmit={handleSubmit(submission)}>
            <Dialog
                open={openCreate}
                onClose={onCloseCreate}
                PaperProps={{
                    component: 'form',
                }}
                fullWidth={true}
            >
                
                <DialogTitle>Create New Portfolio</DialogTitle>
                <DialogContent>
                    <Box sx={{display:'flex', width:'100%', padding:4, flexDirection:'column', justifyContent:'space-around', mt: 1 }}>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 1 }}>
                            <MyTextField
                                label="Name"
                                name="name"
                                control={control}
                                placeholder="Provide a Portfolio Name"
                                width={'100%'}
                            />
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                            <Box>
                            <Typography variant="h7" sx={{ display: 'flex' }}>Level of Risk Aversion:</Typography>
                            <Typography variant="h8" sx={{ display: 'flex' }}></Typography>
                            </Box>
                            <Box sx={{ mt: 2 }}>
                            <SliderField
                                label='Risk Aversion'
                                name='risk_aversion'
                                control={control}
                                width={'100%'}
                                min={0}
                                max={4}
                                step={0.01}
                                marks={marks}
                            />
                            </Box>
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                            <BasicSelectField
                                label='Main Sector' 
                                name='market_index'
                                control={control}
                                width={'100%'}
                                options={options}
                            />
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                            <BasicSelectField
                                label='Investment Time Period Goal' 
                                name='investment_time_period'
                                control={control}
                                width={'100%'}
                                options={timeOptions}
                            />
                        </Box>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onCloseCreate}>Cancel</Button>
                    <Button variant='contained' type='submit'>Submit</Button>
                </DialogActions>
                
            </Dialog>
            </form>
        </>
    )
}
