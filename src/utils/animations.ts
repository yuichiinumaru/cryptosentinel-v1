
import { useEffect, useState } from 'react';

// Creates a staggered array of delays for animations
export const getStaggeredDelay = (index: number, baseDelay: number = 50): number => {
  return index * baseDelay;
};

// Hook for creating fade-in animations
export const useFadeIn = (delay: number = 0) => {
  const [style, setStyle] = useState({ 
    opacity: 0, 
    transform: 'translateY(10px)' 
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setStyle({
        opacity: 1,
        transform: 'translateY(0)',
        transition: 'opacity 0.5s ease, transform 0.5s ease'
      });
    }, delay);
    
    return () => clearTimeout(timer);
  }, [delay]);

  return style;
};

// Hook for reveal on scroll
export const useRevealOnScroll = (
  threshold: number = 0.1
): [React.RefObject<HTMLDivElement>, boolean] => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = React.createRef<HTMLDivElement>();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (ref.current) observer.unobserve(ref.current);
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) observer.unobserve(ref.current);
    };
  }, [ref, threshold]);

  return [ref, isVisible];
};

// Utility for applying blur effects when elements enter/exit
export const blurTransition = (isEntering: boolean) => {
  return {
    initial: { filter: 'blur(8px)', opacity: 0 },
    animate: isEntering 
      ? { filter: 'blur(0px)', opacity: 1 } 
      : { filter: 'blur(8px)', opacity: 0 },
    transition: { duration: 0.4, ease: 'easeOut' }
  };
};

export const slideUpTransition = (delay: number = 0) => {
  return {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    transition: { 
      duration: 0.4, 
      ease: [0.25, 0.1, 0.25, 1.0], 
      delay: delay / 1000 
    }
  };
};
