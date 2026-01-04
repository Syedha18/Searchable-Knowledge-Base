import { useState, useEffect, useMemo } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { SearchBar } from "@/components/SearchBar";
import { DocumentCard } from "@/components/DocumentCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge, FileSearch, FileText, Image, Settings, Table } from "lucide-react";
import { Button } from "@/components/ui/button.tsx";
import { ThemeSelectionPanel } from "@/components/ThemeSelectionPanel.tsx";
import { TableResult } from "@/components/TableResult";
import { Card, CardHeader, CardTitle } from "@/components/ui/card.tsx";

async function searchDocuments(query: string) {
    const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),  // 👈 changed from { q: query }
    });

    if (!res.ok) throw new Error("Search failed");
    return await res.json();
}

const DOCUMENT_BASE_URL = `http://localhost:${8000}/pdfs/`;
const VISUAL_BASE_URL = `http://localhost:${8000}/visuals/`;

export default function Index() {
    const [searchQuery, setSearchQuery] = useState("");
    const [activeTab, setActiveTab] = useState<"pdf" | "image">("pdf");
    const [allResults, setAllResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [isThemePanelOpen, setIsThemePanelOpen] = useState(false);

    const [pdfResults, setPdfResults] = useState<any[]>([]);
    const [imageResults, setImageResults] = useState<any[]>([]);

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        setLoading(true);
        try {
            const data = await searchDocuments(searchQuery.trim());

            // Map text results
            const textResults = (data.text_results || []).map((r: any) => {

                // 1. Construct the full URL with the page jump command
                const pdfUrl = `${DOCUMENT_BASE_URL}${r.file_name}#page=${r.page_number}`;

                return {
                    ...r,

                    type: "pdf",
                    title: r.heading,
                    description: r.text,
                    category: r.file_name,
                    date: `Page ${r.page_number}`,
                    tags: [],

                    // 2. The new onClick handler: opens the URL in a new tab
                    onClick: () => {
                        window.open(pdfUrl, '_blank');
                    }
                }
            });

            // Map visual results
            const visuals = (data.visual_results || []).map((v: any) => {

                const visualUrl = `http://localhost:8000${v.url}`;

                // Extract PDF Name from URL /visuals/<pdf_name>/...
                // URL structure: /visuals/{pdf_name}/{type}/{filename}
                const pathParts = v.url.split('/');
                const pdfName = pathParts[2];
                const sourcePdfUrl = pdfName ? `${DOCUMENT_BASE_URL}${pdfName}.pdf#page=${v.page}` : null;

                return {
                    ...v,
                    type: v.type || "image", // Use backend type (table/image) or default to image
                    title: v.caption || v.filename,
                    description: `Image in ${v.filename}`, // 👈 Generic description for image
                    category: v.filename,
                    date: `Page ${v.page}`, // 👈 Using Page Number here
                    tags: [],
                    // The onClick function that opens the Image is here!
                    sourcePdfUrl, // Pass for backlinking
                    onClick: () => {
                        if (visualUrl) window.open(visualUrl, "_blank");
                        else console.warn("No image URL for", v.filename);
                    }
                }
            });

            const mergedResults = [...textResults, ...visuals];

            setAllResults(mergedResults);
            setPdfResults(textResults);
            setImageResults(visuals);
        } catch (err) {
            console.error("Search error:", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredResults = useMemo(() => {
        return allResults.filter(r =>
            activeTab === "pdf" ? r.type === "text" : (r.type === "image" || r.type === "table")
        );
    }, [allResults, activeTab]);

    return (
        <div className="min-h-screen bg-gradient-subtle">
            {/* Header */}
            <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">

                    {/* Left Side (Logo and Title) - Remains the same */}
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary">
                            <FileSearch className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">Knowledge Base</h1>
                            <p className="text-xs text-muted-foreground">Enterprise Document Library</p>
                        </div>
                    </div>

                    {/* 🔑 THE FIX: Group the controls in a single div */}
                    <div className="flex items-center space-x-2 relative">

                        {/* 1. Theme Toggle (Moon/Sun) */}
                        <ThemeToggle />

                        {/* 2. Settings Button */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="rounded-full"
                            onClick={() => setIsThemePanelOpen(!isThemePanelOpen)}
                        >
                            <Settings className="h-5 w-5" />
                            <span className="sr-only">Select Color Theme</span>
                        </Button>

                        {/* 3. The Minimalist Popover Panel (Conditional Rendering) */}
                        {isThemePanelOpen && (
                            <div
                                // w-40 provides a nice, compact size
                                className="absolute top-12 right-0 w-40 shadow-xl rounded-lg border border-border bg-card p-1 animate-in fade-in-0 slide-in-from-top-1"
                            >
                                <ThemeSelectionPanel onClose={() => setIsThemePanelOpen(false)} />
                            </div>
                        )}
                    </div>
                    {/* 🔑 END OF GROUPED CONTROLS */}

                </div>
            </header>

            {/* Hero Section */}
            <section className="border-b bg-card/30 backdrop-blur-sm">
                <div className="container mx-auto px-4 py-12 md:py-16 text-center">
                    <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                        Search Your Documents
                    </h2>
                    <p className="text-lg text-muted-foreground mb-6">
                        Find what you need from our comprehensive knowledge base
                    </p>
                    <div className="flex justify-center">
                        <SearchBar
                            value={searchQuery}
                            onChange={setSearchQuery}
                            onSubmit={handleSearch}
                        />
                    </div>
                </div>
            </section>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "pdf" | "image")}>
                    <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
                        <TabsList>
                            <TabsTrigger value="pdf" className="gap-2">
                                <FileText className="h-4 w-4" /> PDFs
                            </TabsTrigger>
                            <TabsTrigger value="image" className="gap-2">
                                <Image className="h-4 w-4" /> Images
                            </TabsTrigger>
                        </TabsList>
                        <p className="text-sm text-muted-foreground">
                            {activeTab === "pdf"
                                ? pdfResults.length
                                : imageResults.length}{" "}
                            result{(activeTab === "pdf" ? pdfResults : imageResults).length !== 1 && "s"} found
                        </p>
                    </div>

                    {loading ? (
                        <div className="text-center py-16 text-muted-foreground">Searching...</div>
                    ) : (
                        <>
                            <TabsContent value="pdf">
                                <ResultsGrid items={pdfResults} emptyText="No PDFs found" />
                            </TabsContent>

                            <TabsContent value="image">
                                <ResultsGrid items={imageResults} emptyText="No images found" />
                            </TabsContent>
                        </>
                    )}
                </Tabs>
            </main>
        </div>
    );
}

function ResultsGrid({ items, emptyText }: { items: any[]; emptyText: string }) {
    if (items.length === 0)
        return (
            <div className="flex flex-col items-center justify-center py-16 text-center">
                <FileSearch className="h-16 w-16 text-muted-foreground/50 mb-4" />
                <h3 className="text-xl font-semibold mb-2">{emptyText}</h3>
                <p className="text-muted-foreground">Try adjusting your search</p>
            </div>
        );

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {items.map((item, i) => {
                const isVisual =
                    item.type === "image" ||
                    item.type === "table" ||
                    item.url?.includes("/visuals/");

                // 🖼️ For image/table results
                if (isVisual) {
                    return (
                        <Card
                            key={i}
                            className="group cursor-pointer overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1"
                            onClick={item.onClick}
                        >
                            {/* Image or table preview */}
                            <div className="relative aspect-video overflow-hidden bg-muted">
                                {item.type === "table" ? (
                                    <div className="h-full w-full bg-background">
                                        <TableResult
                                            rows={item.rows}
                                            columns={item.columns}
                                            table_data={item.table_data}
                                            extracted_rows={item.extracted_rows}
                                            caption={item.caption}
                                            filename={item.filename}
                                            page_number={item.page_number}
                                            score={item.score}
                                            url={item.url}
                                            sourcePdfUrl={item.sourcePdfUrl}
                                            onClick={item.onClick}
                                        />
                                    </div>
                                ) : item.type === "image" ? (
                                    <div className="relative h-full w-full">
                                        <img
                                            src={item.url?.startsWith("http") ? item.url : `http://localhost:8000${item.url}`}
                                            alt={item.caption || "Visual preview"}
                                            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                                        />
                                        {/* Backlink Overlay for Images (mimics Table header icon) */}
                                        {item.sourcePdfUrl && (
                                            <div
                                                className="absolute top-2 left-2 z-20 rounded-md bg-secondary/80 p-2 backdrop-blur-sm transition-opacity hover:bg-secondary cursor-pointer"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    window.open(item.sourcePdfUrl, "_blank");
                                                }}
                                                title={`Open PDF at Page ${item.date}`}
                                            >
                                                <FileText className="h-5 w-5 text-secondary-foreground" />
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                                        <Table className="h-10 w-10 opacity-50" />
                                    </div>
                                )}

                            </div>

                        </Card>
                    );
                }

                // 📄 For document/PDF results
                return (
                    <DocumentCard
                        key={i}
                        title={item.title}
                        description={item.description}
                        category={item.category}
                        date={item.date}
                        tags={item.tags}
                        onClick={item.onClick}
                    />
                );
            })}
        </div>
    );
}
