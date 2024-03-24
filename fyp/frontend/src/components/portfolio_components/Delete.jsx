
import {React, useEffect, useState} from "react";
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton } from "@mui/material";
import { Delete as DeleteIcon } from '@mui/icons-material';
import {useForm} from 'react-hook-form';
import useAxios from '../../utils/useAxios';

export default function Delete({ openDelete, onOpenDelete, onCloseDelete, Id }) {
    const [myData, setMydata] = useState([])
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const GetData = async () => {
        try {
            const response = await api.get(`/portfolio/${Id}`)
            setMydata(response.data)
            setLoading(false)
        } catch (error) {
            console.log(error)
            setError(error.response?.data.detail || "An error occurred while fetching the portfolio.")
        }
    }

    useEffect(() => {
        GetData();
    },[])
    const {handleSubmit, reset, setValue, control} = useForm()
    const submission = async (data) => {
        try {
            const response = await api.delete(`portfolio/${Id}/`)
            onCloseDelete()
            window.location.reload();
        } catch (error) {
            setError(error.response?.data.detail || "An error occurred while saving the portfolio.")
            onCloseDelete()
        }
    }
    return (
        <>
            <IconButton color="error" onClick={onOpenDelete}>
                <DeleteIcon />
            </IconButton>
            <form onSubmit={handleSubmit(submission)}>
            <Dialog
                open={openDelete}
                onClose={onCloseDelete}
                PaperProps={{
                    component: 'form',
                }}
                fullWidth={true}
            >
                
                <DialogTitle>Are you sure you want to delete the portfolio: {myData.name}?</DialogTitle>
                <DialogContent>
                    
                </DialogContent>
                <DialogActions>
                    <Button onClick={onCloseDelete}>Cancel</Button>
                    <Button variant='contained' type='submit'>Submit</Button>
                </DialogActions>
                
            </Dialog>
            </form>
        </>
    )
}