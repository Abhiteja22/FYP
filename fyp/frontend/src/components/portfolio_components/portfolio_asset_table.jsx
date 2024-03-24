import { useMemo } from 'react';
import { MRT_GlobalFilterTextField, MRT_TableBodyCellValue, MRT_TablePagination, MRT_ToolbarAlertBanner, flexRender, useMaterialReactTable } from 'material-react-table';
import { Box, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import EditTransaction from './EditTransaction';

export default function PortfolioAssetTable({ data, openEdit, onOpenEdit, onCloseEdit, assets, openDelete, onOpenDelete, onCloseDelete, Id }) {
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
            accessorKey: 'quantity',
            header: 'Quantity'
        },
        {
            accessorKey: 'weight',
            header: 'Weight'
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
        //     //   <DeleteTransaction />
        //     ),
        //   },
        ],
        [],
    );
    const table = useMaterialReactTable({
        columns,
        data: data,
        enablePagination: false,
      });

      return (
            <Stack sx={{ m: '2rem 0' }}>
            <Typography variant="h5">Portfolio current holdings:</Typography>
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
                    <TableRow key={row.id} selected={row.getIsSelected()}>
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