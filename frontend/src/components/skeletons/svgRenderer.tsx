import React from 'react';

interface SVGRendererProps {
    svgContent: string;
}

const SVGRenderer: React.FC<SVGRendererProps> = ({ svgContent }) => {
    const sanitizeSVG = (svg: string): string => {
        return svg
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/\b(on\w+)="[^"]*"/gi, '');
    };
    
    return (
        <span 
            className="inline-block" 
            dangerouslySetInnerHTML={{ __html: sanitizeSVG(svgContent) }}
        />
    );
};

export default SVGRenderer;