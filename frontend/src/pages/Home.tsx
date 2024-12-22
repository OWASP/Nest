import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const Home = () => {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/projects')
  }, [navigate])

  return <div>Hello!</div>
}

export default Home
