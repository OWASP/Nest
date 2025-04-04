import React from 'react';
import DOMPurify from 'dompurify';

interface SVGRendererProps {
    svgContent: string;
}

const SVGRenderer: React.FC<SVGRendererProps> = ({ svgContent }) => {
    const sanitizeSVG = (svg: string): string => {
        return DOMPurify.sanitize(svg, {
            USE_PROFILES: { svg: true, svgFilters: true },
            FORBID_TAGS: ['script'],
            FORBID_ATTR: ['onerror', 'onload', 'onclick']
        });
    };
    
    return (
        <span 
            className="inline-block" 
            dangerouslySetInnerHTML={{ __html: sanitizeSVG(svgContent) }}
        />
    );
};

export default SVGRenderer;