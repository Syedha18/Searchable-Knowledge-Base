import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit?: () => void; // NEW
    placeholder?: string;
}

export function SearchBar({ value, onChange, onSubmit, placeholder = "Search documents..." }: SearchBarProps) {
    return (
        <div className="relative w-full max-w-2xl">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
                type="search"
                placeholder={placeholder}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && onSubmit) {
                        e.preventDefault();
                        onSubmit();
                    }
                }}
                className="h-14 pl-12 pr-4 text-base shadow-md transition-shadow focus-visible:shadow-lg"
            />
        </div>
    );
}

