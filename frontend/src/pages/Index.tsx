import { useState, useMemo } from "react";
import { ThemeToggle } from "@/components/ThemeToggle.tsx";
import { SearchBar } from "@/components/SearchBar.tsx";
import { DocumentCard } from "@/components/DocumentCard.tsx";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockDocuments } from "@/data/mockDocuments";
import { FileSearch, FileText, Image } from "lucide-react";

const Index = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [activeTab, setActiveTab] = useState<"pdf" | "image">("pdf");

    const filteredDocuments = useMemo(() => {
        return mockDocuments.filter((doc) => {
            const matchesSearch =
                searchQuery === "" ||
                doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

            const matchesType = doc.type === activeTab;

            return matchesSearch && matchesType;
        });
    }, [searchQuery, activeTab]);

    return (
        <div className="min-h-screen bg-gradient-subtle">
            {/* Header */}
            <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary">
                            <FileSearch className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">Knowledge Base</h1>
                            <p className="text-xs text-muted-foreground">Enterprise Document Library</p>
                        </div>
                    </div>
                    <ThemeToggle />
                </div>
            </header>

            {/* Hero Section */}
            <section className="border-b bg-card/30 backdrop-blur-sm">
                <div className="container mx-auto px-4 py-12 md:py-16">
                    <div className="mx-auto max-w-3xl text-center space-y-6">
                        <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
                            Search Your Documents
                        </h2>
                        <p className="text-lg text-muted-foreground">
                            Find what you need from our comprehensive knowledge base
                        </p>
                        <div className="flex justify-center pt-4">
                            <SearchBar value={searchQuery} onChange={setSearchQuery} />
                        </div>
                    </div>
                </div>
            </section>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                <Tabs defaultValue="pdf" value={activeTab} onValueChange={(v) => setActiveTab(v as "pdf" | "image")} className="w-full">
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between mb-8">
                        <TabsList className="w-fit">
                            <TabsTrigger value="pdf" className="gap-2">
                                <FileText className="h-4 w-4" />
                                PDFs
                            </TabsTrigger>
                            <TabsTrigger value="image" className="gap-2">
                                <Image className="h-4 w-4" />
                                Images
                            </TabsTrigger>
                        </TabsList>
                        <p className="text-sm text-muted-foreground">
                            {filteredDocuments.length} {filteredDocuments.length === 1 ? "document" : "documents"} found
                        </p>
                    </div>

                    <TabsContent value="pdf" className="mt-0">
                        {filteredDocuments.length > 0 ? (
                            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                                {filteredDocuments.map((doc) => (
                                    <DocumentCard
                                        key={doc.id}
                                        title={doc.title}
                                        description={doc.description}
                                        category={doc.category}
                                        date={doc.date}
                                        tags={doc.tags}
                                        onClick={() => console.log("Open document:", doc.id)}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-16 text-center">
                                <FileSearch className="h-16 w-16 text-muted-foreground/50 mb-4" />
                                <h3 className="text-xl font-semibold mb-2">No PDFs found</h3>
                                <p className="text-muted-foreground">
                                    Try adjusting your search
                                </p>
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="image" className="mt-0">
                        {filteredDocuments.length > 0 ? (
                            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                                {filteredDocuments.map((doc) => (
                                    <DocumentCard
                                        key={doc.id}
                                        title={doc.title}
                                        description={doc.description}
                                        category={doc.category}
                                        date={doc.date}
                                        tags={doc.tags}
                                        onClick={() => console.log("Open document:", doc.id)}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-16 text-center">
                                <FileSearch className="h-16 w-16 text-muted-foreground/50 mb-4" />
                                <h3 className="text-xl font-semibold mb-2">No images found</h3>
                                <p className="text-muted-foreground">
                                    Try adjusting your search
                                </p>
                            </div>
                        )}
                    </TabsContent>
                </Tabs>
            </main>

            {/* Footer */}
            <footer className="border-t bg-card/30 backdrop-blur-sm mt-16">
                <div className="container mx-auto px-4 py-8">
                    <p className="text-center text-sm text-muted-foreground">
                        Enterprise Knowledge Base System
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default Index;
