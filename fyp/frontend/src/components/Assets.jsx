import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import useAxios from '../utils/useAxios';
import { MaterialReactTable, useMaterialReactTable } from 'material-react-table';

const Assets = () => {
    const [assets, setAssets] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true)
    const api = useAxios();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/assets/');
                setAssets(response.data)
                setLoading(false)
            } catch (error) {
                console.log('error')
                setError(error.response?.data.detail || "An error occurred while fetching the assets.");
            }
        };
        fetchData();
    }, []);

    const columns = useMemo(
        () => [
        {
            accessorKey: 'ticker',
            header: 'Ticker',
            enableGrouping: false,
        },
        {
            accessorKey: 'name',
            header: 'Name',
            enableGrouping: false,
        },
        {
            accessorKey: 'exchange',
            header: 'Exchange'
        },
        {
            accessorKey: 'country',
            header: 'Country'
        },
        {
            accessorKey: 'sector',
            header: 'Sector'
        },
        ],
        [],
    );

    const table = useMaterialReactTable({
        columns,
        data: assets,
        enableColumnFilterModes: true,
        enableGrouping: true,
        enableColumnPinning: true,
        enableFacetedValues: true,
        enableFullScreenToggle: false,
        initialState: {
            showColumnFilters: false,
            showGlobalFilter: true,
            columnPinning: {
                left: ['mrt-row-expand', 'mrt-row-select'],
                right: ['mrt-row-actions'],
            },
        },
        paginationDisplayMode: 'pages',
        positionToolbarAlertBanner: 'bottom',
        muiSearchTextFieldProps: {
            size: 'small',
            variant: 'outlined',
        },
        muiPaginationProps: {
            color: 'secondary',
            rowsPerPageOptions: [10, 20, 30],
            shape: 'rounded',
            variant: 'outlined',
        },
        muiTableBodyRowProps: ({ row }) => ({
            onClick: (event) => {
              console.log(row.original.id)
              navigate(`/assets/${row.original.id}`);
            },
            sx: {
              cursor: 'pointer', //you might want to change the cursor too when adding an onClick
            },
          }),
    });

    return (
        <div>
            <h2>Assets</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <ul>
                { loading ? <p>Loading data...</p> :
                    <MaterialReactTable table={table} />
                }
            </ul>
        </div>
    );
};

export default Assets;