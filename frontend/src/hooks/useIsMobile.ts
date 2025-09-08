import { useEffect, useState } from "react"


export const useIsMobile = () => {
    const [isMobile , setIsMobile] = useState<boolean>(false);


    useEffect(() => {
        const mediaQuery = window.matchMedia('(max-width:768px)');

        setIsMobile(mediaQuery.matches);

        const handleChange = (e:MediaQueryListEvent) => setIsMobile(e.matches);
        mediaQuery.addEventListener('change' , handleChange);

        return () => mediaQuery.removeEventListener('change' , handleChange);
    },[])

    return isMobile;

}