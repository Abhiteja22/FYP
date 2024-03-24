import { useMemo } from 'react';
import { MRT_TableBodyCellValue, MRT_ToolbarAlertBanner, flexRender, useMaterialReactTable } from 'material-react-table';
import { Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

export default function OptimizePortfolioTable({ data }) {
    const columns = useMemo(
        () => [
        {
            accessorKey: 'asset_ticker',
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
            header: 'Adjustment'
        },
        {
            accessorKey: 'weight',
            header: 'Target Weight'
        },
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
            <Typography variant="h5">You can optimize portfolio as such:</Typography>
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
                        backgroundColor: row.original.positive ? 'darkgreen' : 'red',
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