import { FileText, Layers, Tag } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface DocumentCardProps {
    title: string;
    description: string;
    category: string;
    date: string;
    tags: string[];
    onClick: () => void;
}

export function DocumentCard({ title, description, category, date, tags, onClick }: DocumentCardProps) {
    return (
        <Card
            className="group cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={onClick}
        >
            <CardHeader className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 text-secondary">
                        <FileText className="h-5 w-5" />
                        <Badge variant="secondary" className="max-w-[175px] font-normal text-secondary-foreground overflow-hidden text-ellipsis whitespace-nowrap">
                            {category} 
                        </Badge>
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Layers className="h-3.5 w-3.5" />
                        {date}
                    </div>
                </div>
                <CardTitle className="line-clamp-2 group-hover:text-primary transition-colors">
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <CardDescription className="line-clamp-3">
                    {description}
                </CardDescription>
                {tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                                <Tag className="mr-1 h-3 w-3" />
                                {tag}
                            </Badge>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
