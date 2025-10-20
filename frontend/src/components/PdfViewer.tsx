import { Document, Page, pdfjs } from "react-pdf";
import { useState } from "react";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

interface PdfViewerProps {
    fileUrl: string;
    highlights?: { page: number; text: string }[];
}

export const PdfViewer: React.FC<PdfViewerProps> = ({ fileUrl}) => {
    const [numPages, setNumPages] = useState<number>(0);

    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    return (
        <div className="pdf-viewer border border-gray-700 rounded-lg p-4 bg-gray-900">
        <Document file={fileUrl} onLoadSuccess={onDocumentLoadSuccess}>
        {Array.from(new Array(numPages), (_, i) => (
                <Page key={i} pageNumber={i + 1} width={800} />
))}
    </Document>
    </div>
);
};
