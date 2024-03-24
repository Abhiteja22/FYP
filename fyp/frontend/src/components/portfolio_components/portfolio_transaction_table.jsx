import { useMemo } from 'react';
import { MRT_GlobalFilterTextField, MRT_TableBodyCellValue, MRT_TablePagination, MRT_ToolbarAlertBanner, flexRender, useMaterialReactTable } from 'material-react-table';
import { Box, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import EditTransaction from './EditTransaction';
import numeral from 'numeral';
import Dayjs from 'dayjs';

export default function PortfolioTransactionTable({ data, openEdit, onOpenEdit, onCloseEdit, assets, openDelete, onOpenDelete, onCloseDelete }) {
    const columns = useMemo(
        () => [
        {
            accessorKey: 'asset_name',
            header: 'Asset Name',
        },
        {
            accessorKey: 'asset_ticker',
            header: 'Asset Ticker',
        },
        {
            accessorKey: 'quantity',
            header: 'Quantity'
        },
        {
            accessorKey: 'value',
            header: 'Value'
        },
        {
            accessorKey: 'transaction_type',
            header: 'BUY/SELL'
        },
        {
            accessorKey: 'transaction_date',
            Cell: ({ value }) => Dayjs(value).format('DD MMMM YYYY'),
            header: 'Date of Transaction'
        },
        // {
        //     accessorKey: 'action',
        //     header: 'Actions',
        //     enableSorting: false,
        //     Cell: ({ row }) => (
        //        <EditTransaction 
        //         openEdit={openEdit}
        //         onOpenEdit={onOpenEdit}
        //         onCloseEdit={onCloseEdit}
        //         Id={Id}
        //         assets={assets}
        //         />
        //        <DeleteTransaction />
        //     ),
        //   },
        ],
        [],
    );
    const table = useMaterialReactTable({
        columns,
        data: data,
        enablePagination: true,
        initialState: {
            pagination: { pageSize: 5, pageIndex: 0 },
          },
          muiPaginationProps: {
            rowsPerPageOptions: [5, 10, 15],
            variant: 'outlined',
          },
          paginationDisplayMode: 'pages',
      });

      return (
            <Stack sx={{ m: '2rem 0' }}>
            <Box
                sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                }}
            >
                <MRT_TablePagination table={table} />
            </Box>
            <Typography variant="h5">Transactions History:</Typography>
            <TableContainer>
                <Table>
                {/* Use your own markup, customize however you want using the power of TanStack Table */}
                <TableHead>
                    {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                        <TableCell align="center" variant="head" key={header.id}>
                            {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.Header ??
                                    header.column.columnDef.header,
                                header.getContext(),
                                )}
                        </TableCell>
                        ))}
                    </TableRow>
                    ))}
                </TableHead>
                <TableBody>
                    {table.getRowModel().rows.map((row, rowIndex) => (
                    <TableRow key={row.id} selected={row.getIsSelected()} sx={{
                        backgroundColor: row.original.transaction_type === 'BUY' ? 'darkgreen' : 'red',
                      }}>
                        {row.getVisibleCells().map((cell, _columnIndex) => (
                        <TableCell align="center" variant="body" key={cell.id}>
                            {/* Use MRT's cell renderer that provides better logic than flexRender */}
                            <MRT_TableBodyCellValue
                            cell={cell}
                            table={table}
                            staticRowIndex={rowIndex} //just for batch row selection to work
                            />
                        </TableCell>
                        ))}
                    </TableRow>
                    ))}
                </TableBody>
                </Table>
            </TableContainer>
            <MRT_ToolbarAlertBanner stackAlertBanner table={table} />
            </Stack>
      )
}