import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';

// --- Constants ---
type Theme = 'slate' | 'teal' | 'gold' | 'rose';
const ALL_THEME_CLASSES = ['theme-teal', 'theme-gold', 'theme-rose'];
const THEME_KEY = 'app-color-theme';


// --- Theme Selection Panel Component ---
// Note: This component assumes it is rendered inside a conditional block (the Popover) 
// and receives a function to close itself (onClose).
export const ThemeSelectionPanel: React.FC<{ onClose: () => void }> = ({ onClose }) => {
    const [currentTheme, setCurrentTheme] = useState<Theme>('slate');

    // 1. Core Logic: Applies the theme class to the <html> tag
    const applyThemeClass = useCallback((theme: Theme) => {
        const htmlEl = document.documentElement;

        // Defensive removal of all color theme classes (preserves 'dark' class)
        ALL_THEME_CLASSES.forEach(c => htmlEl.classList.remove(c));

        if (theme !== 'slate') {
            htmlEl.classList.add(`theme-${theme}`);
        }
        localStorage.setItem(THEME_KEY, theme);
    }, []);

    // 2. Initialization: Load theme on mount (with a small delay for next-themes)
    useEffect(() => {
        // Add a small delay to avoid race conditions with next-themes/ThemeProvider
        const timer = setTimeout(() => {
            const storedTheme = (localStorage.getItem(THEME_KEY) as Theme) || 'slate';
            setCurrentTheme(storedTheme);
            applyThemeClass(storedTheme);
        }, 50);

        return () => clearTimeout(timer); // Cleanup
    }, [applyThemeClass]);

    // 3. Selection Handler
    const handleThemeChange = (newTheme: Theme) => {
        setCurrentTheme(newTheme);
        applyThemeClass(newTheme);
        onClose(); // 🔑 Close the panel immediately after a theme is selected!
    };

    // --- Render the List UI ---
    return (
        <div className="w-full">
            <h4 className="text-sm font-semibold mb-2 px-3 pt-1 border-b border-border/50 pb-1">
                Color Themes
            </h4>

            <div className="flex flex-col space-y-1">
                {['slate', 'teal', 'gold', 'rose'].map(theme => (
                    <Button
                        key={theme}
                        variant={currentTheme === theme ? "default" : "ghost"}
                        onClick={() => handleThemeChange(theme as Theme)}
                        className="capitalize justify-start text-sm h-9 px-3"
                    >
                        {theme === 'slate' ? 'Default' : theme}
                    </Button>
                ))}
            </div>
        </div>
    );
};