import EntityExampleComponent from "./EntityExampleComponent"
import Footer from "./components/Footer";
import ModeToggle from "./components/ModeToggle";

function App() {
  return (
    <div className="w-full h-full flex flex-col justify-between items-start bg-background text-text  ">
      <ModeToggle className=" fixed top-0 right-0 " />
      <EntityExampleComponent />
      <Footer/>
    </div>
  )
}

export default App
