import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { fetchHeatmapData, drawContributions, HeatmapData } from 'utils/helpers/githubHeatmap'

const HeatMap = ({ className = '' }: { className?: string }) => {
  const { userKey } = useParams()
  const [data, setData] = useState<HeatmapData | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [imageLink, setImageLink] = useState('')
  const [username, setUsername] = useState('')
  const [privateContributor, setPrivateContributor] = useState(false)
  const theme = 'blue'

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchHeatmapData(userKey)
      if (result && result.contributions) {
        setUsername(userKey)
        setData(result)
      } else {
        setPrivateContributor(true)
      }
    }
    fetchData()
  }, [userKey])

  useEffect(() => {
    if (canvasRef.current && data && data.years && data.years.length > 0) {
      drawContributions(canvasRef.current, { data, username, theme })
      const imageURL = canvasRef.current.toDataURL()
      setImageLink(imageURL)
    }
  }, [username, data])

  return (
    <div className={`bg-gray-900 relative h-32 items-center justify-center ${className}`}>
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
      {privateContributor ? (
        <div className="h-32 bg-owasp-blue"></div>
      ) : imageLink ? (
        <div className="bg-#10151c h-32">
          <img src={imageLink} className="h-full w-full object-cover object-[54%_60%]" />
        </div>
      ) : (
        <div className="bg-#10151c relative h-32 items-center justify-center">
          <img
            src="/img/heatmapBackground.png"
            className="heatmap-background-loader h-full w-full border-none object-cover object-[54%_60%]"
          />
          <div className="heatmap-loader"></div>
        </div>
      )}
    </div>
  )
}

export default HeatMap
