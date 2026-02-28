import DOMPurify from 'isomorphic-dompurify'
import React from 'react'
import { ProfilePageStructuredData } from 'types/profilePageStructuredData'

interface StructuredDataScriptProps {
  data: ProfilePageStructuredData
}

const StructuredDataScript: React.FC<StructuredDataScriptProps> = ({ data }) => {
  const cleanData = DOMPurify.sanitize(JSON.stringify(data, null, 2))
  return (
    <script
      id="profile-structured-data"
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: cleanData,
      }}
    />
  )
}

export default StructuredDataScript
