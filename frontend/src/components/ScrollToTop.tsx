import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp } from '@fortawesome/free-solid-svg-icons';

export default function ScrollToTop() {
  const [isVisible, setIsVisible] = useState(false);

  const handleScroll = () => {
    const scrollThreshold = window.innerHeight * 0.3;
    setIsVisible(window.pageYOffset > scrollThreshold);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <button
      onClick={scrollToTop}
      aria-label="Scroll to top"
      className={`fixed bottom-4 right-4 flex items-center justify-center w-12 h-12 bg-owasp-blue bg-opacity-70 text-white dark:text-slate-300 rounded-full shadow-lg transition-all duration-400 active:scale-100 hover:scale-105 hover:bg-opacity-100 dark:bg-opacity-30 hover:dark:bg-opacity-50
        ${isVisible ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
    >
      <FontAwesomeIcon icon={faArrowUp} className="text-xl" />
    </button>
  );
}
