import { useEffect, useRef } from "react";

type Props = {
  text: string;
  autoPlay?: boolean;
};

export default function TextToSpeech({ text, autoPlay = false }: Props) {
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const speak = () => {
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    utteranceRef.current = utterance;

    window.speechSynthesis.speak(utterance);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
  };

  useEffect(() => {
    if (autoPlay && text) {
      speak();
    }

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [text, autoPlay]);

  return (
    <div>
      <button onClick={speak}>🔊 Listen</button>
      <button onClick={stop}>⏹ Stop</button>
    </div>
  );
}