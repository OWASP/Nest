
import { Routes, Route } from "react-router-dom";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Home from "./pages/Home";
import Projects from "./pages/Projects";

function App() {
  return (
    <main className=" flex flex-col justify-start w-full min-h-screen m-0 ">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<Projects />}></Route>
      </Routes>
      <Footer />
    </main>
  );
}

export default App
