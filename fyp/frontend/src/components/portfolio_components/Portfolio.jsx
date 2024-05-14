import { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import useAxios from '../../utils/useAxios';
import { Container, Grid, Typography, Box, Button } from '@mui/material';
import MiniWidget from '../widgets/MiniWidget';
import LargeWidget from '../widgets/LargeWidget';
import Chart from '../widgets/Chart';
import PortfolioAssetTable from './portfolio_asset_table';
import PortfolioTransactionTable from './portfolio_transaction_table';
import numeral from 'numeral';
import Dayjs from 'dayjs';
import AddAsset from './AddAsset';


const Portfolio = () => {
    const param = useParams();
    const portfolioId = param.id
    const [assets, setAssets] = useState([])
    const [portfolio, setPortfolio] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true)
    const api = useAxios();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`portfolio/${portfolioId}/`);
                const response2 = await api.get(`/assets`)
                setAssets(response2.data)
                setPortfolio(response.data)
                setLoading(false)
            } catch (error) {
                setError(error.response?.data.detail || "An error occurred while fetching the assets.");
            }
        };
        fetchData();
    }, []);
    useEffect(() => {
      console.log(portfolio); // This will log whenever `portfolio` changes
  }, [portfolio]);
    const [openAdd, setOpenAdd] = useState(false);

    const handleOpenAdd = () => {
      setOpenAdd(true);
    };

    const handleCloseAdd = () => {
      setOpenAdd(false);
    }
    const [openEdit, setOpenEdit] = useState(false);

    const handleOpenEdit = () => {
      setOpenEdit(true);
    };

    const handleCloseEdit = () => {
      setOpenEdit(false);
    }
    const [openDelete, setOpenDelete] = useState(false);

    const handleOpenDelete = () => {
      setOpenDelete(true);
    };

    const handleCloseDelete = () => {
      setOpenDelete(false);
    }
    const [openOptimize, setOpenOptimize] = useState(false);

    const handleOpenOptimize = () => {
      setOpenOptimize(true);
    };

    const handleCloseOptimize = () => {
      setOpenOptimize(false);
    }
    return (
        <Container maxWidth="xl">
        { loading ? <p>Loading data...</p> :
        <Container maxWidth="xl" sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column'}}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
                <Typography variant="h4">
                    {portfolio.name}
                </Typography>
                <Box>
                <AddAsset
                    openAdd={openAdd}
                    onOpenAdd={handleOpenAdd}
                    onCloseAdd={handleCloseAdd}
                    Id = {portfolio.id}
                    assets = {assets}
                    existingAssets={portfolio.current_assets_held}
                    oldest_date_asset_bought={portfolio.oldest_date_asset_bought}
                    />
                  </Box>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
              <Typography variant="h5" sx={{ mb: 2 }}>
                  Created On: {Dayjs(portfolio.creation_date).format('DD MMMM YYYY')}
              </Typography>
              <Box>
                  <Button variant="contained" component={Link} to={`/optimize/${portfolio.id}`} state={{ portfolio }}>
                    Analyse Portfolio
                  </Button>
                  </Box>
                </Box>
            </Box>
        
  
        <Grid container spacing={3}>
            <Grid item xs={12}>
            <PortfolioAssetTable
                data={portfolio.current_assets_held}
                openEdit={openEdit}
                onOpenEdit={handleOpenEdit}
                onCloseEdit={handleCloseEdit}
                assets={assets}
                openDelete={openDelete}
                onOpenDelete={handleOpenDelete}
                onCloseDelete={handleCloseDelete}
                Id={portfolio.id}
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
              title="Invested in Current Holdings"
              total={numeral(portfolio.invested_currently).format('$0,0.00')}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <LargeWidget
              title="Profit to date"
              description={numeral(portfolio.profit_to_date).format('$0,0.00')}
              description2={numeral(portfolio.percentage_profit).format('0.000%')}
              positive={portfolio.percentage_profit >= 0}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <MiniWidget
              title="Beta"
              total={numeral(portfolio.beta).format('0.000')}
              color="info"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <MiniWidget
              title="Standard Deviation"
              total={numeral(portfolio.standard_deviation).format('0.000%')}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <MiniWidget
                title="Expected Return"
                total={numeral(portfolio.expected_return).format('0.000%')}
                color="success"
            />
          </Grid>

           <Grid item xs={12} sm={6} > {/*sx={{ display: { lg: 'none' } }} */}
            <MiniWidget
                title="Sharpe Ratio"
                total={numeral(portfolio.sharpe_ratio).format('0.000')}
                color="success"
            />
          </Grid>

          {/* <Grid item lg={4} sx={{ display: { xs: 'none', lg: 'block' } }} container spacing={3} direction="column" justifyContent="space-between" alignItems="center">
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
          </Grid> */}
  
          {/* <Grid item xs={12} lg={8}>
            <Chart
              title="Price History"
            />
          </Grid> */}
  
          <Grid item xs={12} sm={6}>
            <LargeWidget
                title="Sector"
                description={portfolio.sector}
                description2={`Based on: ${portfolio.market_index_long_name}`}
                color="success"
                positive={true}
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <MiniWidget
                title="Time Period Goal"
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
          <Grid item xs={12}>
            <PortfolioTransactionTable
                data={portfolio.transactions}
                openEdit={openEdit}
                onOpenEdit={handleOpenEdit}
                onCloseEdit={handleCloseEdit}
                assets={assets}
                openDelete={openDelete}
                onOpenDelete={handleOpenDelete}
                onCloseDelete={handleCloseDelete}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <MiniWidget
              title="Money Invested"
              total={numeral(portfolio.money_invested).format('$0,0.00')}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <MiniWidget
              title="Money Withdrawn"
              total={numeral(portfolio.money_withdrawn).format('$0,0.00')}
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