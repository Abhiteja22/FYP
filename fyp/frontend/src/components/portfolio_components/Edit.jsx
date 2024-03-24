
import {React, useEffect, useState} from "react";
import { Box, Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Typography } from "@mui/material";
import { Edit as EditIcon } from '@mui/icons-material';
import MyTextField from "../forms/MyTextField";
import {useForm} from 'react-hook-form';
import useAxios from '../../utils/useAxios';
import SliderField from "../forms/SliderField";
import BasicSelectField from "../forms/BasicSelectField";
import { marks, options, timeOptions, defaultValues } from "./portfolio_constants";

export default function Edit({ openEdit, onOpenEdit, onCloseEdit, Id }) {
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const GetData = async () => {
        try {
            const response = await api.get(`/portfolio/${Id}`)
            setValue('name', response.data.name)
            setValue('risk_aversion', response.data.risk_aversion)
            setValue('market_index', response.data.market_index)
            setValue('investment_time_period', response.data.investment_time_period)
            setLoading(false)
        } catch (error) {
            console.log(error)
            setError(error.response?.data.detail || "An error occurred while fetching the portfolio.")
        }
    }

    useEffect(() => {
        GetData();
    },[])

    const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues})
    const submission = async (data) => {
        try {
            // Find the option object that matches the submitted market_index value
            const selectedOption = options.find(option => option.value === data.market_index);
        
            // Extract the label from the selected option. If no option is found, default to an empty string or a placeholder value
            const sectorLabel = selectedOption ? selectedOption.label : '';
            const response = await api.put(`portfolio/${Id}/`, {
                name: data.name,
                risk_aversion: data.risk_aversion,
                market_index: data.market_index,
                sector: sectorLabel,
                investment_time_period: data.investment_time_period,
            })
            onCloseEdit()
            window.location.reload();
        } catch (error) {
            setError(error.response?.data.detail || "An error occurred while saving the portfolio.")
            onCloseEdit()
        }
    }

    return (
        <>
            <IconButton color="secondary" onClick={onOpenEdit}>
                <EditIcon />
            </IconButton>
            <form onSubmit={handleSubmit(submission)}>
            <Dialog
                open={openEdit}
                onClose={onCloseEdit}
                PaperProps={{
                    component: 'form',
                }}
                fullWidth={true}
            >
                
                <DialogTitle>Edit Portfolio Details</DialogTitle>
                <DialogContent>
                    { loading ? <p>Loading data...</p> :
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
                    }
                </DialogContent>
                <DialogActions>
                    <Button onClick={onCloseEdit}>Cancel</Button>
                    <Button variant='contained' type='submit'>Submit</Button>
                </DialogActions>
                
            </Dialog>
            </form>
        </>
    )
}