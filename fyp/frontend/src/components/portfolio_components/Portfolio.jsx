import { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import useAxios from '../../utils/useAxios';
import { Container, Grid, Typography, Box } from '@mui/material';
import MiniWidget from '../widgets/MiniWidget';
import LargeWidget from '../widgets/LargeWidget';
import Chart from '../widgets/Chart';
import PortfolioAssetTable from './portfolio_asset_table';
import numeral from 'numeral';
import Dayjs from 'dayjs';

const Portfolio = () => {
    const param = useParams();
    const portfolioId = param.id
    const [portfolio, setPortfolio] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true)
    const api = useAxios();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`portfolio/${portfolioId}/`);
                setPortfolio(response.data)
                setLoading(false)
            } catch (error) {
                setError(error.response?.data.detail || "An error occurred while fetching the assets.");
            }
        };
        fetchData();
    }, []);

    return (
        <Container maxWidth="xl">
        { loading ? <p>Loading data...</p> :
        <Container maxWidth="xl" sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column'}}>
            <Typography variant="h4" sx={{ mb: 5 }}>
                {portfolio.name}
            </Typography>
            <Typography variant="h4" sx={{ mb: 5 }}>
                Created On: {Dayjs(portfolio.creation_date).format('DD MMMM YYYY')}
            </Typography>
            </Box>
        
  
        <Grid container spacing={3}>
            <Grid item xs={12}>
            <PortfolioAssetTable
                data={portfolio.portfolio_asset_details}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <MiniWidget
              title="Current Value"
              total={numeral(portfolio.portfolio_value).format('$0,0.00')}
              color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={4}>
            <MiniWidget
              title="Beta"
              total={numeral(portfolio.beta).format('0.000')}
              color="info"
            />
          </Grid>
  
          <Grid item xs={12} sm={4}>
            <MiniWidget
              title="Standard Deviation"
              total={numeral(portfolio.standard_deviation).format('0.000%')}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} sx={{ display: { lg: 'none' } }}>
            <MiniWidget
                title="Expected Return"
                total={numeral(portfolio.expected_return).format('0.000%')}
                color="success"
            />
          </Grid>

          <Grid item xs={12} sm={6} sx={{ display: { lg: 'none' } }}>
            <MiniWidget
                title="Sharpe Ratio"
                total={numeral(portfolio.sharpe_ratio).format('0.000')}
                color="success"
            />
          </Grid>

          <Grid item lg={4} sx={{ display: { xs: 'none', lg: 'block' } }} container spacing={3} direction="column" justifyContent="space-between" alignItems="center">
            <Grid item xs={4}>
                <MiniWidget
                    title="Expected Return"
                    total={numeral(portfolio.expected_return).format('0.000%')}
                    color="success"
                />
            </Grid>
            <Grid item xs={4}>
                <MiniWidget
                    title="Sharpe Ratio"
                    total={numeral(portfolio.sharpe_ratio).format('0.000')}
                    color="success"
                />
            </Grid>
          </Grid>
  
          <Grid item xs={12} lg={8}>
            <Chart
              title="Price History"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <LargeWidget
                title="Sector"
                description={portfolio.sector}
                description2={`Based on: ${portfolio.market_index_long_name}`}
                color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <MiniWidget
                title="Industry"
                total={portfolio.investment_time_period}
                color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <LargeWidget
              title="Status"
              description={portfolio.status}
              description2={portfolio.sell_date}
              color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <MiniWidget
              title="Risk Aversion"
              total={portfolio.risk_aversion}
              color="info"
            />
          </Grid>
        </Grid>
        </Container>
        }
      </Container>
    );
};

export default Portfolio;