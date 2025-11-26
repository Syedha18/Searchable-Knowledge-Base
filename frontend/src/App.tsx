import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import React, { useState } from 'react';
import ChatWidget from "@/components/ChatWidget.tsx"; // Renamed from RougeCoderChat

const queryClient = new QueryClient();

// Define the fixed width for the drawer and the margin
const DRAWER_WIDTH_CLASS = 'mr-[40vw]';

// Convert to a component that can hold state (using explicit return)
const App = () => {
    // State of the chat drawer is managed here, at the highest level
    const [isChatOpen, setIsChatOpen] = useState(false);

    return (
        <>
            {/* 1. Main Content Wrapper (Applies the push margin) */}
            <div
                className={`transition-all duration-500 ease-in-out ${isChatOpen ? DRAWER_WIDTH_CLASS : 'mr-0'}`}
            >
                {/* All your app providers and content routes go inside the push container */}
                <QueryClientProvider client={queryClient}>
                    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
                        <TooltipProvider>
                            <Sonner />
                            <BrowserRouter>
                                <Routes>
                                    <Route path="/" element={<Index />} />
                                    {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                                    <Route path="*" element={<NotFound />} />
                                </Routes>
                            </BrowserRouter>
                        </TooltipProvider>
                    </ThemeProvider>
                </QueryClientProvider>
            </div>

            {/* 2. Chat Widget (Fixed position, controls its own slide/visibility) */}
            <ChatWidget isOpen={isChatOpen} setIsOpen={setIsChatOpen} />
        </>
    );
};

export default App;