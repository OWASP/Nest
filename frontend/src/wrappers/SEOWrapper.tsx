import React from 'react'
import { SEOWrapperProps } from 'types/seo'
import MetadataManager from 'components/MetadataManager'

const SEOWrapper: React.FC<SEOWrapperProps> = ({
  title,
  description,
  keywords,
  image,
  type,
  url,
  children,
}) => {
  return (
    <>
      <MetadataManager
        title={title}
        description={description}
        keywords={keywords}
        image={image}
        type={type}
        url={url}
      />
      {children}
    </>
  )
}

export default SEOWrapper
