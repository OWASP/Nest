import { useState, useEffect } from "react";
import { cn } from "../lib/utils";

function ModeToggle({ className }: { className?: string }) {
    const [dark, setDark] = useState(() => {
        return localStorage.getItem("theme") === "dark";
    });

    useEffect(() => {
        if (dark) {
            document.body.classList.add("dark");
        } else {
            document.body.classList.remove("dark");
        }
    }, [dark]);

    const darkModeHandler = () => {
        setDark(!dark);
        const newTheme = !dark ? "dark" : "light";
        document.body.classList.toggle("dark", !dark);
        localStorage.setItem("theme", newTheme);
    };

    return (
        <div className={cn("", className)}>
            <button onClick={darkModeHandler} className=" flex justify-center items-center p-1 ">
                {dark ? <i className="fa-solid fa-moon"></i> : <i className="fa-regular fa-lightbulb"></i>}
            </button>
        </div>
    );
}

export default ModeToggle;
