
import { useState, useEffect, CSSProperties } from 'react';

type FadeInStyle = {
  opacity: number;
  transform: string;
};

export const useFadeIn = (delay: number = 0): CSSProperties => {
  const [style, setStyle] = useState<FadeInStyle>({
    opacity: 0,
    transform: 'translateY(20px)'
  });

  useEffect(() => {
    const timeout = setTimeout(() => {
      setStyle({
        opacity: 1,
        transform: 'translateY(0)'
      });
    }, delay);
    
    return () => clearTimeout(timeout);
  }, [delay]);

  return {
    opacity: style.opacity,
    transform: style.transform,
    transition: 'opacity 0.5s ease-out, transform 0.5s ease-out'
  } as CSSProperties;
};

export const useTypingEffect = (text: string, speed: number = 50): string => {
  const [displayedText, setDisplayedText] = useState('');
  
  useEffect(() => {
    let currentIndex = 0;
    setDisplayedText('');
    
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(prev => prev + text.charAt(currentIndex));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, speed);
    
    return () => clearInterval(interval);
  }, [text, speed]);
  
  return displayedText;
};
