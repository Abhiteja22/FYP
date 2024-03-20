
import {React, useState, useEffect} from "react";
import { useParams, useLocation } from 'react-router-dom';
import { Button, Container, Grid, Typography } from "@mui/material";
import {useForm} from 'react-hook-form';
import useAxios from '../../utils/useAxios';
import OptimizePortfolioTable from "./optimize_portfolio_table";
import { useNavigate } from "react-router-dom";
import AIResponse from "../widgets/AIResponse";
import SpinnerLoader from "../widgets/SpinnerLoader";

function formatToPreviousWeekday(date) {
    const dayOfWeek = date.getDay(); // 0 is Sunday, 6 is Saturday
    let adjustedDate = new Date(date);

    if (dayOfWeek === 0) { // Sunday
        // Move to previous Friday
        adjustedDate.setDate(date.getDate() - 2);
    } else if (dayOfWeek === 6) { // Saturday
        // Move to previous Friday
        adjustedDate.setDate(date.getDate() - 1);
    }
    
    // Format the date as 'yyyy-MM-dd'
    const year = adjustedDate.getFullYear();
    const month = (adjustedDate.getMonth() + 1).toString().padStart(2, '0');
    const day = adjustedDate.getDate().toString().padStart(2, '0');

    return `${year}-${month}-${day}`;
}

export default function OptimizePortfolio() {
    const location = useLocation();
    const { portfolio } = location.state;
    const param = useParams();
    const Id = param.id
    const [error, setErrors] = useState('')
    const [optimzedAssets, setoptimzedAssets] = useState([]);
    const [loading, setLoading] = useState(true)
    const [loading2, setLoading2] = useState(true)
    const [loading3, setLoading3] = useState(true)
    const [optimize, setOptimize] = useState(false)
    const [suggest, setSuggest] = useState('')
    const [weights, setWeights] = useState([])
    const [aiResponse, setAiResonse] = useState('')
    const api = useAxios();
    const GetOptimizeData = async () => {
      try {
          const response = await api.get(`/optimize/${Id}`)
          setoptimzedAssets(response.data)
          setLoading(false)
      } catch (error) {
          console.log(error)
          setErrors(error.response?.data.detail || "An error occurred while fetching the portfolio.")
      }
  }
  const GetRimentAIData = async () => {
    try {
        const response = await api.post('/rimentai/', {
          portfolio: portfolio // Make sure this matches the expected structure on the backend
        });
        setAiResonse(response.data)
        setLoading2(false)
    } catch (error) {
        console.log(error)
        setErrors(error.response?.data.detail || "An error occurred while fetching the portfolio.")
    }
}
const GetRimentSuggestData = async () => {
    try {
        const response = await api.post('/suggest/', {
          time_period: portfolio.investment_time_period,
          sector: portfolio.sector,
          assets_held: portfolio.current_assets_held,
          risk_aversion: portfolio.risk_aversion
        });
        setSuggest(response.data.response)
        setWeights(response.data.weights)
        setLoading3(false)
    } catch (error) {
        console.log(error)
        setErrors(error.response?.data.detail || "An error occurred while fetching the portfolio.")
    }
}
useEffect(() => {
    (async () => {
        await GetOptimizeData();
        await GetRimentAIData();
        await GetRimentSuggestData();
    })();
}, []);
useEffect(() => {
    if (Array.isArray(optimzedAssets)) {
        optimzedAssets.forEach(transaction => {
            if (transaction.quantity_numerical > 0) {
                setOptimize(true);
            }
        });
    }
}, [optimzedAssets]);
const navigate = useNavigate()
    const {handleSubmit } = useForm()
    const submission = async (data) => {
        for (const transaction of optimzedAssets.optimized_weights) {
            const { asset_ticker, adjustment, quantity_numerical, id } = transaction;
            if (quantity_numerical == 0) continue;
            // Find the asset ID based on the ticker
    
            // Prepare transaction data
            const transactionData = {
                portfolio: Id, // Assuming Id is the portfolio ID
                asset: id,
                transaction_type: adjustment.toUpperCase(), // 'BUY' or 'SELL'
                quantity: quantity_numerical,
                transaction_date: formatToPreviousWeekday(new Date()), // Current date or from UI
            };
    
            // Submit the transaction
            try {
                await api.post('transaction/', transactionData);
                console.log('Transaction submitted for', asset_ticker);
            } catch (error) {
                console.error('Error submitting transaction for', asset_ticker, error);
                // Handle error (e.g., show a message to the user)
            }
        }
        navigate(`/portfolios/${Id}`)
        window.location.reload();
    }
    const submission2 = async (data) => {
        for (const transaction of optimzedAssets.optimized_weights) {
            const { asset_ticker, adjustment, quantity_numerical, id } = transaction;
            if (quantity_numerical == 0) continue;
            // Find the asset ID based on the ticker
    
            // Prepare transaction data
            const transactionData = {
                portfolio: Id, // Assuming Id is the portfolio ID
                asset: id,
                transaction_type: adjustment.toUpperCase(), // 'BUY' or 'SELL'
                quantity: quantity_numerical,
                transaction_date: formatToPreviousWeekday(new Date()), // Current date or from UI
            };
    
            // Submit the transaction
            try {
                await api.post('transaction/', transactionData);
                console.log('Transaction submitted for', asset_ticker);
            } catch (error) {
                console.error('Error submitting transaction for', asset_ticker, error);
                // Handle error (e.g., show a message to the user)
            }
        }
        navigate(`/portfolios/${Id}`)
        window.location.reload();
    }
    return (
        <>
            <Container maxWidth="xl">
            
            <Container maxWidth="xl" sx={{ mb: 4 }}>
            {/* <Typography>Loading data... Might take a few seconds to optimize</Typography> */}
            <Grid container spacing={3}>
            { loading ? (<Grid item xs={12}><SpinnerLoader /></Grid>) :
                (<>
                    { optimize ? (
                    <Grid item xs={12}>()
                <OptimizePortfolioTable
                    data={optimzedAssets.optimized_weights}
                /><form onSubmit={handleSubmit(submission)}>
                <Button variant='contained' type='submit'>Confirm Optimization?</Button></form></Grid>)
                :
                        (<Grid item xs={12}>
                            <AIResponse
                            title={'Optimize'}
                            description={'Your portfolio is already optimized to the highest sharpe ratio.'}
                            />
                        </Grid>)  
                    }
                    </>)
                }
                { loading2 ? <Grid item xs={12}><SpinnerLoader /></Grid> : (
                <Grid item xs={12}>
                <AIResponse
                    title={'RimentAI'}
                    description={aiResponse ? aiResponse.response : 'Loading Response'}
                />
                </Grid>)
                }
                { loading2 ? <Grid item xs={12}><SpinnerLoader /></Grid> :
                <Grid item xs={12}>
                <AIResponse
                    title={'RimentAI Suggestion'}
                    description={suggest ? suggest : 'Loading Response...It will take a few minutes'}
                />
                {/* <form onSubmit={handleSubmit(submission2)}>
                <Button variant='contained' type='submit'>Set as portfolio?</Button></form> */}
                </Grid>
                }   
            </Grid>
            </Container>
            </Container>
        </>
    )
}
