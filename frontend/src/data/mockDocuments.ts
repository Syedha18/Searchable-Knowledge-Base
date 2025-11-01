export interface Document {
    id: string;
    title: string;
    description: string;
    category: string;
    date: string;
    tags: string[];
    content: string;
    type: "pdf" | "image";
}

export const mockDocuments: Document[] = [
    {
        id: "1",
        title: "Enterprise Security Guidelines 2024",
        description: "Comprehensive security protocols and best practices for enterprise-level applications, including authentication, authorization, and data protection strategies.",
        category: "Security",
        date: "2024-01-15",
        tags: ["security", "compliance", "best-practices"],
        content: "Full document content would be here...",
        type: "pdf"
    },
    {
        id: "2",
        title: "Cloud Infrastructure Best Practices",
        description: "Guidelines for deploying and managing cloud infrastructure at scale, covering AWS, Azure, and GCP platforms with cost optimization strategies.",
        category: "Infrastructure",
        date: "2024-01-10",
        tags: ["cloud", "devops", "aws"],
        content: "Full document content would be here...",
        type: "pdf"
    },
    {
        id: "3",
        title: "API Design Standards v3.0",
        description: "RESTful API design standards including versioning, error handling, pagination, and documentation requirements for all enterprise services.",
        category: "Development",
        date: "2024-01-05",
        tags: ["api", "standards", "rest"],
        content: "Full document content would be here...",
        type: "pdf"
    },
    {
        id: "4",
        title: "Data Privacy Compliance Manual",
        description: "GDPR and CCPA compliance guidelines for handling customer data, including data retention policies and user consent management.",
        category: "Legal",
        date: "2023-12-20",
        tags: ["gdpr", "privacy", "compliance"],
        content: "Full document content would be here...",
        type: "pdf"
    },
    {
        id: "5",
        title: "Performance Optimization Guide",
        description: "Strategies for optimizing application performance including caching, database indexing, and frontend optimization techniques.",
        category: "Development",
        date: "2023-12-15",
        tags: ["performance", "optimization", "caching"],
        content: "Full document content would be here...",
        type: "pdf"
    },
    {
        id: "6",
        title: "System Architecture Diagram",
        description: "Comprehensive system architecture diagram showing microservices, databases, and infrastructure components.",
        category: "Infrastructure",
        date: "2023-12-01",
        tags: ["architecture", "diagram", "infrastructure"],
        content: "Full document content would be here...",
        type: "image"
    },
    {
        id: "7",
        title: "API Flow Diagrams",
        description: "Visual representation of API request/response flows, authentication sequences, and data transformation pipelines.",
        category: "Development",
        date: "2023-11-25",
        tags: ["api", "diagram", "flow"],
        content: "Full document content would be here...",
        type: "image"
    },
    {
        id: "8",
        title: "Database Schema Visualization",
        description: "Entity relationship diagram showing all database tables, relationships, and key constraints.",
        category: "Development",
        date: "2023-11-20",
        tags: ["database", "schema", "diagram"],
        content: "Full document content would be here...",
        type: "image"
    },
    {
        id: "9",
        title: "Security Threat Model",
        description: "Visual threat model identifying potential security vulnerabilities and attack vectors across the system.",
        category: "Security",
        date: "2023-11-15",
        tags: ["security", "threat", "diagram"],
        content: "Full document content would be here...",
        type: "image"
    },
];
