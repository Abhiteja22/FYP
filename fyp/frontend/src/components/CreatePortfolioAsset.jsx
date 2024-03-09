
import {React, useEffect, useState} from "react";
import { Box, Typography, Button } from "@mui/material";
import MyTextField from "./forms/MyTextField";
import MyNumberField from "./forms/MyNumberField";
import BasicSelectField from "./forms/BasicSelectField";
import {useForm} from 'react-hook-form';
import AxiosInstance from '../utils/Axios';
import { useNavigate } from "react-router-dom";
import { yupResolver } from "@hookform/resolvers/yup"
import * as yup from "yup"

const CreatePortfolioAsset = () => {

    const [portfolio, setPortfolio] = useState([])
    const [loading, setLoading] = useState(true)
    const GetData = () => {
        AxiosInstance.get(`portfolio/`).then((res) => {
            setPortfolio(res.data)
            console.log(res.data)
            setLoading(false)
        })
    }

    useEffect(() => {
        GetData();
    },[])

    const navigate = useNavigate()
    const defaultValues = {
        asset_ticker: 'AAPL',
        quantity: 1,
    }
    const schema = yup
    .object({
        asset_ticker: yup.string().required('Asset ticker is a required field'),
        quantity: yup.number().required('Quantity is a required field'),
        portfolio: yup.string().required('Portfolio is a required field')
    })
    const {handleSubmit, reset, setValue, control} = useForm({defaultValues:defaultValues, resolver: yupResolver(schema)})
    const submission = (data) => {
        AxiosInstance.post(`portfolioAsset/`, {
            asset_ticker: data.asset_ticker,
            quantity: data.quantity,
            portfolio: data.portfolio,
        })
        .then((res) => {
            navigate(`/`)
        })
    }
    return (
        <div>
            { loading ? <p>Loading data...</p> :
            <form onSubmit={handleSubmit(submission)}>
            <Box sx={{display:'flex', width:'100%', backgroundColor:'#00003f', marginBottom:'10px'}}>
                <Typography sx={{marginLeft:'20px', color:'#fff'}}>
                    Add Portfolio Asset
                </Typography>
            </Box>

            <Box sx={{display:'flex', width:'100%', boxShadow:3, padding:4, flexDirection:'column'}}>
                <Box sx={{display:'flex', justifyContent:'space-around', marginBottom: '40px'}}>
                    <MyTextField
                      label="Asset Ticker"
                      name="asset_ticker"
                      control={control}
                      placeholder="Provide a Asset Ticker Symbol"
                      width={'30%'}
                    />
                    <MyNumberField
                      label="Quantity"
                      name="quantity"
                      control={control}
                      placeholder="Provide Quantity of assets"
                      width={'30%'}
                    />
                    <BasicSelectField
                      label="Portfolio"
                      name="portfolio"
                      control={control}
                      width={'30%'}
                      placeholder="Select a portfolio"
                      options= {portfolio}
                    />
                </Box>
                <Box sx={{display:'flex', justifyContent:'start', marginTop: '40px'}}>
                    <Button variant='contained' type='submit' sx={{width:'30%'}}>
                        Submit
                    </Button>
                </Box>
            </Box>
            </form>
            }
        </div>
    )
}

export default CreatePortfolioAsset