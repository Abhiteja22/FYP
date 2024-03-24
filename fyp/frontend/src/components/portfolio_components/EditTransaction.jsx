
import {React, useState, useEffect} from "react";
import { Box, Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton } from "@mui/material";
import { Edit as EditIcon } from '@mui/icons-material';
import MyTextField from "../forms/MyTextField";
import {useForm} from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup"
import useAxios from '../../utils/useAxios';
import * as yup from "yup"
import { defaultValues, transactionOptions } from "./portfolio_constants";
import AutocompleteField from "../forms/AutocompleteField";
import DateField from "../forms/DateField";
import BasicSelectField from "../forms/BasicSelectField";

export default function EditTransaction({ openEdit, onOpenEdit, onCloseEdit, Id, assets }) {
    const [error, setError] = useState('')
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const GetData = async () => {
        try {
            const response = await api.get(`/transaction/${transactionId}`)
            setValue('asset', response.data.asset)
            setValue('transaction_type', response.data.transaction_type)
            setValue('quantity', response.data.quantity)
            setValue('transaction_date', response.data.transaction_date)
            setLoading(false)
        } catch (error) {
            console.log(error)
            setError(error.response?.data.detail || "An error occurred while fetching the portfolio.")
        }
    }
    useEffect(() => {
        GetData();
    },[])
    useEffect(() => {
        setOptions(assets.map(asset => ({
            label: asset.name,
            ticker: asset.ticker,
            id: asset.id
        })));
    }, [assets]);

    const schema = yup.object({
        asset: yup.mixed().oneOf(options.map(option => option.id), 'Asset must be a valid selection').required('Asset is required'),
        transaction_type: yup.string().oneOf(['BUY', 'SELL'], 'transaction_type must be either "BUY" or "SELL"').required('transaction_type is a required field'),
        quantity: yup.number().min(1, 'Quantity must be greater than 0').required('Quantity is required'),
        transaction_date: yup.date().required('Transaction date is required'),
    }).required();
    const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues, resolver: yupResolver(schema)})
    const submission = async (data) => {
        try {
            const response = await api.put(`transaction/`, {
                portfolio: Id,
                asset: data.asset,
                transaction_type: data.transaction_type,
                quantity: data.quantity,
                transaction_date: data.transaction_date
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
            
            <Dialog
                open={openEdit}
                onClose={onCloseEdit}
                fullWidth={true}
            >
                <form onSubmit={handleSubmit(submission)}>
                
                <DialogTitle>Edit Asset Transaction</DialogTitle>
                <DialogContent>
                { loading ? <p>Loading data...</p> :
                    <Box sx={{display:'flex', width:'100%', pEditing:4, flexDirection:'column', justifyContent:'space-around', mt: 1 }}>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 1 }}>
                            <AutocompleteField
                                label="Asset"
                                name="asset"
                                control={control}
                                width={'100%'}
                                options={options}
                            />
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                        <MyTextField
                                label="Quantity"
                                name="quantity"
                                control={control}
                                placeholder="Provide a Quantity"
                                width={'100%'}
                            />
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                        <BasicSelectField
                            label="Transaction Type"
                            name='transaction_type'
                            control={control}
                            width={'100%'}
                            options={transactionOptions}
                            />
                        </Box>
                        <Box sx={{display:'flex', justifyContent:'space-around', mt: 2, flexDirection: 'column' }}>
                            <DateField
                                label='Date Bought' 
                                name='transaction_date'
                                control={control}
                            />
                        </Box>
                    </Box>
}
                </DialogContent>
                <DialogActions>
                    <Button onClick={onCloseEdit}>Cancel</Button>
                    <Button variant='contained' type='submit'>Submit</Button>
                </DialogActions>
                </form>
            </Dialog>
            
        </>
    )
}
