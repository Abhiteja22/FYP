import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import useAxios from '../../utils/useAxios';
import { Container, Grid, Typography } from '@mui/material';
import AssetWidgetSummary from './asset_widget_summary';
import AssetPriceHistory from './asset_price_history_chart';
import numeral from 'numeral';

const Asset = () => {
    const param = useParams();
    const assetId = param.id
    const [asset, setAsset] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`assets/${assetId}/`);
                setAsset(response.data)
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
        <Typography variant="h4" sx={{ mb: 5 }}>
          {asset.name} ({asset.ticker})
        </Typography>
  
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <AssetWidgetSummary
              title="Current Price"
              total={numeral(asset.current_price).format('$0,0.00')}
              color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={4}>
            <AssetWidgetSummary
              title="Beta"
              total={numeral(asset.beta).format('0.000')}
              color="info"
            />
          </Grid>
  
          <Grid item xs={12} sm={4}>
            <AssetWidgetSummary
              title="Standard Deviation"
              total={numeral(asset.standard_deviation).format('0.000%')}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} sx={{ display: { lg: 'none' } }}>
            <AssetWidgetSummary
                title="Expected Return"
                total={numeral(asset.expected_return).format('0.000%')}
                color="success"
            />
          </Grid>

          <Grid item xs={12} sm={6} sx={{ display: { lg: 'none' } }}>
            <AssetWidgetSummary
                title="Sharpe Ratio"
                total={numeral(asset.sharpe_ratio).format('0.000')}
                color="success"
            />
          </Grid>

          <Grid item lg={4} sx={{ display: { xs: 'none', lg: 'block' } }} container spacing={3} direction="column" justifyContent="space-between" alignItems="center">
            <Grid item xs={4}>
                <AssetWidgetSummary
                    title="Expected Return"
                    total={numeral(asset.expected_return).format('0.000%')}
                    color="success"
                />
            </Grid>
            <Grid item xs={4}>
                <AssetWidgetSummary
                    title="Sharpe Ratio"
                    total={numeral(asset.sharpe_ratio).format('0.000')}
                    color="success"
                />
            </Grid>
          </Grid>
  
          <Grid item xs={12} lg={8}>
            <AssetPriceHistory
              title="Price History"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
                title="Sector"
                total={asset.sector}
                color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
                title="Industry"
                total={asset.industry}
                color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
              title="Country"
              total={asset.country}
              color="success"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
              title="IPO Year"
              total={asset.ipoYear}
              color="info"
            />
          </Grid>
  
          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
              title="Exchange"
              total={asset.exchange}
              color="warning"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <AssetWidgetSummary
              title="Asset Type"
              total={asset.asset_type}
              color="warning"
            />
          </Grid>

          <Grid item xs={12}>
            <AssetWidgetSummary
              title="Description of Asset"
              total={"random"}
              color="warning"
            />
          </Grid>
        </Grid>
        <Typography variant='h5' sx={{ mt: 3 }}>Current Holdings:</Typography>
        </Container>
        }
      </Container>
    );
};

export default Asset;