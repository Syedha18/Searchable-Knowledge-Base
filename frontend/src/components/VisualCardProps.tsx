import { Image as ImageIcon, Table, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface VisualCardProps {
    type: "image" | "table";
    caption?: string;
    page?: number;
    url: string;
    score?: number;
    onClick?: () => void;
}

export function VisualCard({ type, caption, page, url, score, onClick }: VisualCardProps) {
    const Icon = type === "table" ? Table : ImageIcon;

    return (
        <Card
            className="group cursor-pointer overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={onClick}
        >
            {/* 🖼️ Image Preview */}
            <div className="relative aspect-video overflow-hidden bg-muted">
                {type === "image" ? (
                    <img
                        src={url}
                        alt={caption || "Visual preview"}
                        className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                ) : (
                    <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                        <Table className="h-10 w-10 opacity-50" />
                    </div>
                )}
                {score && (
                    <Badge className="absolute top-2 right-2 bg-primary text-white shadow">
                        {(score * 100).toFixed(0)}%
                    </Badge>
                )}
            </div>
            <CardContent />
        </Card>
    );
}
