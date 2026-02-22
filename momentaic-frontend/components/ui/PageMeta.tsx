import { useEffect } from 'react';

interface PageMetaProps {
    title: string;
    description?: string;
}

export function PageMeta({ title, description }: PageMetaProps) {
    useEffect(() => {
        // Set document title
        document.title = `${title} | MomentAIc`;

        // Set meta description
        if (description) {
            let metaDescription = document.querySelector('meta[name="description"]');
            if (!metaDescription) {
                metaDescription = document.createElement('meta');
                metaDescription.setAttribute('name', 'description');
                document.head.appendChild(metaDescription);
            }
            metaDescription.setAttribute('content', description);
        }

        // Cleanup function (optional, but good practice if you want to revert, 
        // usually in an SPA we just let the next route override it)
        return () => {
            // Reverting to default is handled by the next component mounting.
        };
    }, [title, description]);

    return null; // This component doesn't render anything visible
}
