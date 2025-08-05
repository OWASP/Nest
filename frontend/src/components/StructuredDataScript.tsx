import React from 'react'
import { ProfilePageStructuredData } from 'types/profilePageStructuredData'

interface StructuredDataScriptProps {
  data: ProfilePageStructuredData
}

// dangerouslySetInnerHTML injects the JSON data as a script tag.
const StructuredDataScript: React.FC<StructuredDataScriptProps> = ({ data }) => {
  return (
    <script
      id="profile-structured-data"
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data, null, 2), // include everything with 2 spaces indentation
      }}
    />
  )
}

export default StructuredDataScript
