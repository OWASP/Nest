const Home = () => {
  return (
    <div className="h-screen">
      <div className="flex flex-row justify-between bg-slate-800 h-[4rem] text-2xl items-center p-[2rem] text-white ">
        <a
          className="hover:text-gray-500 hover:underline transition-all ease-in-out duration-300"
          href="https://nest.owasp.dev/projects/contribute/"
        >
          Projects
        </a>
        <a
          className="hover:text-gray-500 hover:underline transition-all ease-in-out duration-300"
          href="https://nest.owasp.dev/chapters/"
        >
          Chapters
        </a>
        <a
          className="hover:text-gray-500 hover:underline transition-all ease-in-out duration-300"
          href="https://nest.owasp.dev/committees/"
        >
          Committees
        </a>
      </div>
    </div>
  );
};

export default Home;
