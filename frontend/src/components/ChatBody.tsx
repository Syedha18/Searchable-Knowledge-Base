// components/ChatBody.tsx
import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// --- (Message Type Definition - Import this from your types file if you made one) ---
export type Message = {
    id: string;
    role: 'user' | 'bot';
    content: string;
    timestamp: Date;
};


interface ChatBodyProps {
    messages: Message[];
}

export const ChatBody: React.FC<ChatBodyProps> = ({ messages }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to the bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // The CSS for markdown rendering (tailoring the Tailwind classes for the markdown output)
    const markdownStyles = `
    prose prose-sm dark:prose-invert max-w-none 
    [&>p]:leading-relaxed 
    [&>ul]:list-disc [&>ul]:pl-5
    [&>ol]:list-decimal [&>ol]:pl-5
    [&>code]:bg-muted/50 [&>code]:p-1 [&>code]:rounded-sm 
    [&>pre]:p-3 [&>pre]:rounded-lg [&>pre]:bg-muted/70 [&>pre]:border [&>pre]:border-border
  `;

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background">
            {messages.map((message) => (
                <div
                    key={message.id}
                    // Align user messages to the right, bot messages to the left
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                        // Styling the bubbles using your HSL variables
                        className={`
              max-w-[80%] p-3 rounded-xl shadow-md text-sm
              ${message.role === 'user'
                            ? 'bg-secondary text-secondary-foreground rounded-br-sm' // Primary color for user (Blue in default theme)
                            : 'bg-card text-foreground border border-border rounded-tl-sm' // Card color for bot
                        }
            `}
                    >
                        {message.role === 'bot' ? (
                            // AI/Bot messages get ReactMarkdown rendering
                            <div className={markdownStyles}>
                                <ReactMarkdown
                                    // Now ReactMarkdown only receives its required props
                                    remarkPlugins={[remarkGfm]}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            </div>
                        ) : (
                            // User messages are plain text
                            <p>{message.content}</p>
                        )}

                        {/* Optional: Timestamp for detail */}
                        <div className="text-[10px] opacity-60 mt-1">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    </div>
                </div>
            ))}
            {/* Scroll target for auto-scrolling */}
            <div ref={messagesEndRef} />
        </div>
    );
};