import { useEffect } from "react"


export default function Projects() {

    useEffect(()=>{
        document.title = "OWASP Projects"
        const fetchApiData = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/v1/owasp/search/project?q=`)
                const data = await response.json()
                console.log(data)
           } catch (error) {
                console.log(error)
            }
        }
        fetchApiData()
    },[])

  return (
    <div className=" w-full min-h-screen flex flex-col justify-normal items-center text-text p-5 md:p-20 ">

    </div>
  )
}
