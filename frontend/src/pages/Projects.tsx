import { useEffect, useState } from "react"
import { ProjectDataType } from "../lib/types";
import FontAwesomeIconWrapper from "../lib/FontAwesomeIconWrapper";
import { getFilteredIcons } from "../lib/utils";
import Card from "../components/EntityComponent/Card";
import { level } from "../components/EntityComponent/data";


export default function Projects() {
    const [projectData, setProjectData] = useState<ProjectDataType | null>(null);

    const handleButtonClick = () => {
        console.log("Button clicked");
      }

    const SubmitButton = {
        label: "Contribute",
        icon: <FontAwesomeIconWrapper icon="fa-solid fa-code-fork" />,
        onclick: handleButtonClick,
    }

    useEffect(()=>{
        document.title = "OWASP Projects"
        const fetchApiData = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/v1/owasp/search/project?q=""')
                const data = await response.json()
                console.log(data)
                setProjectData(data)
            } catch (error) {
                console.log(error)
            }
        }
        fetchApiData()
    },[])

  return (
    <div className=" w-full min-h-screen flex flex-col justify-normal items-center text-text p-5 md:p-20 ">
      <div className=" w-full h-fit flex flex-col justify-normal items-center gap-4 ">
          {
            projectData && projectData.projects.map((project) => {
              const params: string[] = ["idx_updated_at", "idx_forks_count", "idx_stars_count", "idx_contributors_count"];
              const filteredIcons = getFilteredIcons(project, params);
              return (
                <Card
                  key={project.objectID}
                  title={project.idx_name}
                  summary={project.idx_summary}
                  level={level[`${project.idx_level as keyof typeof level}`]}
                  icons={filteredIcons}
                  leaders={project.idx_leaders}
                  topContributors={project.idx_top_contributors}
                  topics={project.idx_topics}
                  button={SubmitButton}
                />
              )
            })
          }
      </div>
    </div>
  )
}
