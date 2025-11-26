// ChatWidget.tsx
import { X } from "lucide-react";
import React from 'react';
import {ChatBody} from "@/components/ChatBody.tsx";
import {useState} from "react";
import {API_BASE_URL} from "@/config.ts";
import {MessageCircle} from "lucide-react";

// Define the props interface
interface ChatWidgetProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
}

const BOT_SESSION_ID = "vicky_session_123";

const initialMessages: Message[] = [
    {
        id: '1',
        role: 'bot',
        content: "Hey vicky, Ask me anything from the SKB",
        timestamp: new Date()
    }
];

export type Message = {
    id: string;
    role: 'user' | 'bot'; // 'user' for Vicky, 'bot' for the AI
    content: string; // The message text, potentially containing markdown
    timestamp: Date;
    isStreaming?: boolean;
};

export default function ChatWidget({ isOpen, setIsOpen }: ChatWidgetProps) {

    const [messages, setMessages] = useState<Message[]>(initialMessages);

    const [input, setInput] = useState('');

    const [isLoading, setIsLoading] = useState(false);
    

    const handleSendMessage = async () => {
        // 1. Initial Checks and Setup
        if (!input.trim() || isLoading) return;

        const userQuery = input.trim();

        // Clear the input and set loading state immediately
        setInput('');
        setIsLoading(true);

        // 2. Prepare and Add User Message Placeholder
        const newUserMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: userQuery,
            timestamp: new Date()
        };

        // 3. Prepare and Add Streaming Bot Placeholder
        const newBotMessagePlaceholder: Message = {
            id: (Date.now() + 1).toString(),
            role: 'bot',
            content: '',
            timestamp: new Date(),
            isStreaming: true, // Crucial flag for finding the message during streaming
        };

        // Update state with both user message and bot placeholder
        setMessages(prev => [...prev, newUserMessage, newBotMessagePlaceholder]);

        // --- Streaming Fetch ---
        try {
            // 🚨 FIX: Use 'const' for the response variable
            const response = await fetch(API_BASE_URL + '/stream_query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userQuery,
                    session_id: BOT_SESSION_ID
                })
            });

            if (!response.ok || !response.body) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let done = false;
            let buffer = ''; // Buffer for robust JSONL processing

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;

                if (value) {
                    const chunk = decoder.decode(value);
                    buffer += chunk; // Add chunk to buffer

                    const parts = buffer.split('\n');
                    buffer = parts.pop() || ''; // Save incomplete part for next loop

                    // Process all complete JSON lines in 'parts'
                    parts.forEach(line => {
                        if (line.trim()) {
                            try {
                                const data = JSON.parse(line);

                                setMessages(prev => {
                                    // Find the streaming message by its last position and flag
                                    const lastMessageIndex = prev.length - 1;
                                    const lastMessage = prev[lastMessageIndex];

                                    // Only update if the message is the correct streaming placeholder
                                    if (lastMessage && lastMessage.isStreaming) {
                                        let updatedContent = lastMessage.content;

                                        if (data.event === 'stream' && data.reply_chunk) {
                                            updatedContent += data.reply_chunk;
                                        }

                                        // 🚨 Termination condition: 'end' or 'error' from server
                                        if (data.event === 'error' || data.event === 'end') {
                                            // 🚀 CRITICAL FIX: Spread lastMessage to maintain id, timestamp, etc.
                                            return [
                                                ...prev.slice(0, lastMessageIndex),
                                                {
                                                    ...lastMessage,
                                                    content: updatedContent,
                                                    isStreaming: false // Finalize message
                                                }
                                            ];
                                        }

                                        // Regular stream update: only update content
                                        return [
                                            ...prev.slice(0, lastMessageIndex),
                                            {
                                                ...lastMessage, // Maintain all original properties
                                                content: updatedContent
                                            }
                                        ];
                                    }
                                    return prev; // Do nothing if we can't find the streaming message
                                });
                            } catch (e) {
                                console.warn("Could not parse JSON line:", line, e);
                            }
                        }
                    });
                }
            }

        } catch (error) {
            console.error("Chat API Error:", error);
            // Add a clean error message to the history
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now().toString(),
                    role: 'bot',
                    content: `Sorry, a connection error occurred. (${error instanceof Error ? error.message : 'Unknown error'})`,
                    timestamp: new Date(),
                    isStreaming: false
                }
            ]);
        } finally {
            // 🚨 CRITICAL CLEANUP BLOCK
            setIsLoading(false);
            // Final check to ensure the isStreaming flag is turned off, regardless of how the 'try' block exited.
            setMessages(prev => {
                const lastMessageIndex = prev.length - 1;
                const lastMessage = prev[lastMessageIndex];

                if (lastMessage && lastMessage.isStreaming) {
                    // 🚀 CRITICAL FIX: Finalize the message with isStreaming: false
                    return [ ...prev.slice(0, lastMessageIndex), { ...lastMessage, isStreaming: false } ];
                }
                return prev;
            });
        }
    };

    // Function to handle the Enter key press
    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };
    
    return (
        <>
            {/* 1. Toggle Button (Always fixed on the right of the whole viewport) */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    // Floating button styling
                    className="fixed bottom-6 right-6 p-4 rounded-full shadow-lg transition
                               bg-secondary text-secondary-foreground hover:bg-primary/90 z-[51]"
                >
                    <MessageCircle />
                </button>
            )}

            {/* 2. Chat Panel (The Drawer) */}
            <div
                // The crucial line: fixed position, 40% width, dynamic sliding
                className={`
                    fixed top-0 right-0 h-full w-[40vw] bg-card border-l border-border shadow-2xl z-50 flex flex-col 
                    transition-transform duration-500 ease-in-out
                    ${isOpen ? 'translate-x-0' : 'translate-x-full'} 
                `}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border bg-card/50 text-foreground">
                    <h2 className="text-lg font-semibold text-primary">
                        Chat
                    </h2>
                    <button
                        onClick={() => setIsOpen(false)} // Call the setter prop to close the drawer
                        className="text-muted-foreground hover:text-foreground transition"
                    >
                        <X size={20} />
                    </button>
                </div>

                <ChatBody messages={messages} />

                {/* --- Input Area Render (Updated) --- */}
                <div className="border-t border-border p-4 bg-card/50">
                    <input
                        type="text"
                        placeholder={isLoading ? "Bot is thinking..." : "Ask the Bot..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress} // Attach the Enter key handler
                        disabled={isLoading} // Disable input while streaming
                        className="w-full bg-input text-foreground px-4 py-2 rounded-lg 
                         focus:outline-none focus:ring-2 focus:ring-primary border border-input 
                         transition disabled:opacity-70 disabled:cursor-not-allowed"
                    />
                </div>

            </div>
        </>
    );
}