import { Table as TableIcon, Loader2, Maximize2, X } from "lucide-react";
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface TableResultProps {
    rows?: number;
    columns?: number;
    table_data?: string[][]; // Full 2D array data if available
    extracted_rows?: any[];  // Structured rows if available
    caption?: string;
    filename?: string;
    page_number?: number;
    score?: number;
    url?: string;
    sourcePdfUrl?: string; // New Prop
    onClick?: () => void;
}

// Robust CSV Parser that handles quoted newlines
function parseCSV(text: string): string[][] {
    const rows: string[][] = [];
    let currentRow: string[] = [];
    let currentCell = "";
    let insideQuotes = false;

    // Normalize newlines
    const raw = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

    for (let i = 0; i < raw.length; i++) {
        const char = raw[i];
        const nextChar = raw[i + 1];

        if (char === '"') {
            if (insideQuotes && nextChar === '"') {
                // Escaped quote ("") -> single quote
                currentCell += '"';
                i++; // Skip next quote
            } else {
                // Toggle quote state
                insideQuotes = !insideQuotes;
            }
        } else if (char === ',' && !insideQuotes) {
            // End of cell
            currentRow.push(currentCell.trim());
            currentCell = "";
        } else if (char === '\n' && !insideQuotes) {
            // End of row
            currentRow.push(currentCell.trim());
            if (currentRow.length > 0 && (currentRow.length > 1 || currentRow[0] !== "")) {
                rows.push(currentRow);
            }
            currentRow = [];
            currentCell = "";
        } else {
            currentCell += char;
        }
    }

    // Push last cell/row if exists
    if (currentCell || currentRow.length > 0) {
        currentRow.push(currentCell.trim());
        rows.push(currentRow);
    }

    return rows;
}

export function TableResult({
    rows,
    columns,
    table_data,
    extracted_rows,
    caption,
    filename,
    page_number,
    score,
    url,
    sourcePdfUrl,
    onClick
}: TableResultProps) {
    const [fetchedData, setFetchedData] = useState<string[][]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    useEffect(() => {
        if (!table_data && !extracted_rows && url && fetchedData.length === 0) {
            setIsLoading(true);
            const fetchUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`;

            fetch(fetchUrl)
                .then(res => res.text())
                .then(text => {
                    const parsed = parseCSV(text);
                    setFetchedData(parsed);
                })
                .catch(err => console.error("Failed to fetch table CSV", err))
                .finally(() => setIsLoading(false));
        }
    }, [url, table_data, extracted_rows]);

    // Determine the data source to use
    let headers: string[] = [];
    let bodyRows: string[][] = [];

    if (table_data && table_data.length > 0) {
        headers = table_data[0];
        bodyRows = table_data.slice(1);
    } else if (fetchedData.length > 0) {
        headers = fetchedData[0];
        bodyRows = fetchedData.slice(1);
    } else if (extracted_rows && extracted_rows.length > 0) {
        headers = Object.keys(extracted_rows[0]);
        bodyRows = extracted_rows.map(row => Object.values(row).map(v => String(v)));
    } else if (columns && rows) {
        // Fallback: Create placeholder grid
        headers = Array(columns).fill("Header");
        bodyRows = Array(rows > 5 ? 5 : rows).fill(Array(columns).fill("Data"));
    }

    const TableContent = ({ isScrollable = true }) => (
        <div className={`w-full ${isScrollable ? "overflow-auto no-scrollbar" : ""}`}>
            <table className="w-full text-sm text-left border-collapse border border-border">
                <thead className="bg-muted text-muted-foreground sticky top-0 z-10">
                    <tr>
                        {headers.map((h, i) => (
                            <th key={i} className="p-4 font-semibold border-b border-r border-border last:border-r-0 min-w-[150px] whitespace-pre-wrap align-top bg-muted">
                                {h}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {bodyRows.length > 0 ? (
                        bodyRows.map((row, rI) => (
                            <tr key={rI} className="border-b border-border last:border-0 hover:bg-muted/20 even:bg-muted/5 transition-colors">
                                {row.map((cell, cI) => (
                                    <td key={cI} className="p-4 border-r border-border last:border-r-0 min-w-[150px] whitespace-pre-wrap align-top break-words">
                                        {cell}
                                    </td>
                                ))}
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan={headers.length || 1} className="p-8 text-center text-muted-foreground">
                                {isLoading ? (
                                    <div className="flex items-center justify-center gap-2">
                                        <Loader2 className="h-4 w-4 animate-spin" /> Loading data...
                                    </div>
                                ) : "Table Preview Not Available"}
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    return (
        <>
            <Card
                className="group relative cursor-pointer overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1 h-full flex flex-col"
                onClick={(e) => {
                    e.stopPropagation();
                    setIsExpanded(true);
                }}
            >
                {/* Header */}
                <div className="relative bg-muted/30 border-b p-3 flex items-center gap-2">
                    {sourcePdfUrl ? (
                        <a
                            href={sourcePdfUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="rounded-md bg-secondary/20 p-2 hover:bg-secondary transition-colors cursor-pointer"
                            onClick={(e) => e.stopPropagation()}
                            title="Open Source PDF"
                        >
                            <TableIcon className="h-5 w-5 text-secondary-foreground" />
                        </a>
                    ) : (
                        <div className="rounded-md bg-secondary/20 p-2">
                            <TableIcon className="h-5 w-5 text-secondary-foreground" />
                        </div>
                    )}
                    <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium truncate" title={caption || filename}>
                            {caption || filename || "Table Result"}
                        </h3>
                        <div className="flex gap-2 text-xs text-muted-foreground">
                            {page_number && <span>Page {page_number}</span>}
                            {rows && columns && <span>{rows}x{columns}</span>}
                        </div>
                    </div>

                    {/* Expand Button (stops propagation to prevent opening file) */}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 ml-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                            e.stopPropagation();
                            setIsExpanded(true);
                        }}
                        title="View Full Table"
                    >
                        <Maximize2 className="h-4 w-4" />
                    </Button>

                </div>

                <CardContent className="p-0 flex-1 overflow-hidden relative min-h-[150px]">
                    <div className="absolute inset-0 z-10 pointer-events-none shadow-[inset_0_-20px_20px_-10px_rgba(0,0,0,0.05)]" />
                    <div className="h-full w-full">
                        <TableContent isScrollable={true} />
                    </div>
                </CardContent>
            </Card>

            {/* Expanded Modal Overlay */}
            {isExpanded && createPortal(
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4 animate-in fade-in-0"
                    onClick={(e) => e.stopPropagation()} // Stop bubbling to parent components
                >
                    <div className="bg-card border shadow-2xl rounded-xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95">
                        <div className="flex items-center justify-between p-4 border-b">
                            <h3 className="text-lg font-semibold">{caption || filename || "Table Viewer"}</h3>
                            <Button variant="ghost" size="icon" onClick={() => setIsExpanded(false)}>
                                <X className="h-5 w-5" />
                            </Button>
                        </div>
                        <div className="flex-1 overflow-auto p-0">
                            <TableContent isScrollable={false} />
                        </div>
                        <div className="p-4 border-t bg-muted/20 flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setIsExpanded(false)}>Close</Button>
                            <Button onClick={() => { if (onClick) onClick(); }}>Download / Open</Button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    );
}
