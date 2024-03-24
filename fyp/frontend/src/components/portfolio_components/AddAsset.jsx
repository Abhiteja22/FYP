
import {React, useState, useEffect} from "react";
import { Box, Button, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import MyTextField from "../forms/MyTextField";
import BasicSelectField from "../forms/BasicSelectField";
import {useForm} from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup"
import useAxios from '../../utils/useAxios';
import * as yup from "yup"
import { defaultValues2, transactionOptions } from "./portfolio_constants";
import AutocompleteField from "../forms/AutocompleteField";
import DateField from "../forms/DateField";
import { format } from 'date-fns';

export default function AddAsset({ openAdd, onOpenAdd, onCloseAdd, Id, assets, existingAssets, oldest_date_asset_bought }) {
    const [error, setErrors] = useState('')
    const [options, setOptions] = useState([]);
    const api = useAxios();
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
    const {handleSubmit, reset, setValue, control, setError, clearErrors } = useForm({defaultValues:defaultValues2, resolver: yupResolver(schema)})
    const submission = async (data) => {
        clearErrors();
        if (data.transaction_type === 'SELL') {
            const asset = assets.find(a => a.id === data.asset);
            if (!asset) {
                setError('asset', { type: 'custom', message: 'Asset not found.' });
                return;
            }
            const assetTicker = asset.ticker;
            const existingAsset = existingAssets.find(a => a.ticker === assetTicker);
            const existingAssetQuantity = existingAsset ? existingAsset.quantity : 0;
            const oldestPurchaseDate = oldest_date_asset_bought[assetTicker];
            const transactionDate = new Date(data.transaction_date);
            const oldestDate = new Date(oldestPurchaseDate);
            if (!existingAsset) {
                setError('asset', { type: 'custom', message: 'Asset not part of portfolio.' });
                return;
            }
            if (data.quantity > existingAssetQuantity) {
                setError('quantity', { type: 'custom', message: 'Selling quantity exceeds available quantity.' });
                return;
            }
            if (transactionDate < oldestDate) {
                setError('transaction_date', { type: 'custom', message: 'Transaction date is before the oldest purchase date.' });
                return;
            }
        }
        if (data.transaction_date) {
            data.transaction_date = format(new Date(data.transaction_date), 'yyyy-MM-dd');
        }
        try {
            const response = await api.post('transaction/', {
                portfolio: Id,
                asset: data.asset,
                transaction_type: data.transaction_type,
                quantity: data.quantity,
                transaction_date: data.transaction_date
            })
            onCloseAdd()
            window.location.reload();
        } catch (error) {
            setErrors(error.response?.data.detail || "An error occurred while saving the portfolio.")
            onCloseAdd()
        }
    }
    return (
        <>
            <Button variant="contained" onClick={onOpenAdd}>
                  Add New Transaction
            </Button>
            
            <Dialog
                open={openAdd}
                onClose={onCloseAdd}
                fullWidth={true}
            >
                <form onSubmit={handleSubmit(submission)}>
                
                <DialogTitle>Add New Transaction</DialogTitle>
                <DialogContent>
                
                    <Box sx={{display:'flex', width:'100%', padding:4, flexDirection:'column', justifyContent:'space-around', mt: 1 }}>
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
                                label='Date Bought/Sold' 
                                name='transaction_date'
                                control={control}
                            />
                        </Box>
                    </Box>
                    
                </DialogContent>
                <DialogActions>
                    <Button onClick={onCloseAdd}>Cancel</Button>
                    <Button variant='contained' type='submit'>Submit</Button>
                </DialogActions>
                </form>
            </Dialog>
            
        </>
    )
}
