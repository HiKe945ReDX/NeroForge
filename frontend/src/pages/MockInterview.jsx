import React, { useState, useRef } from 'react';
import { Mic, MicOff, Play, RotateCcw } from 'lucide-react';

export default function MockInterview() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(null);
  const mediaRecorderRef = useRef(null);
  const recognitionRef = useRef(null);

  const startInterview = () => {
    if (recognitionRef.current) return;
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event) => {
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript_segment = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setTranscript(prev => prev + transcript_segment + ' ');
        } else {
          interimTranscript += transcript_segment;
        }
      }
    };
    recognition.onend = () => setIsRecording(false);
    recognition.start();
    recognitionRef.current = recognition;
  };

  const stopRecording = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    
    try {
      const res = await fetch('https://guidora-backend-746485305795.us-central1.run.app/api/interview/mock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ career: 'Software Engineer', transcript }),
      });
      const data = await res.json();
      setFeedback(data);
      setScore(data.score);
    } catch (e) {
      setFeedback({ feedback: 'Demo mode: Great answer!', score: 78 });
      setScore(78);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <h1 className="text-4xl font-bold text-white mb-2">🎙️ Mock Interview</h1>
      <p className="text-slate-300 mb-8">Practice your interview with AI feedback</p>

      {!score ? (
        <div className="bg-slate-700 rounded-lg p-8 max-w-2xl mx-auto text-white">
          <p className="mb-6 text-lg">Question: Tell me about your most recent project.</p>
          
          <div className="mb-6 p-4 bg-slate-600 rounded">
            <p>{transcript || 'Your answer will appear here...'}</p>
          </div>

          {!isRecording ? (
            <button
              onClick={startInterview}
              className="px-8 py-4 bg-red-600 text-white rounded font-bold flex items-center gap-3 hover:bg-red-500 mx-auto"
            >
              <Mic size={24} /> Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="px-8 py-4 bg-red-600 text-white rounded font-bold flex items-center gap-3 hover:bg-red-500 mx-auto animate-pulse"
            >
              <MicOff size={24} /> Stop & Get Feedback
            </button>
          )}
        </div>
      ) : (
        <div className="bg-slate-700 rounded-lg p-8 max-w-2xl mx-auto text-white">
          <h2 className="text-2xl font-bold mb-6">📊 Interview Feedback</h2>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-600 p-4 rounded text-center">
              <p className="text-slate-300">Overall Score</p>
              <p className="text-4xl font-bold text-emerald-400">{score}%</p>
            </div>
            <div className="bg-slate-600 p-4 rounded text-center">
              <p className="text-slate-300">Technical</p>
              <p className="text-3xl font-bold text-blue-400">82%</p>
            </div>
            <div className="bg-slate-600 p-4 rounded text-center">
              <p className="text-slate-300">Communication</p>
              <p className="text-3xl font-bold text-yellow-400">75%</p>
            </div>
          </div>
          <p className="mb-6 text-slate-300">{feedback?.feedback}</p>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="font-bold text-emerald-400 mb-2">✓ Strengths</p>
              <ul className="text-slate-300 space-y-1">
                {feedback?.strengths?.map((s, i) => <li key={i}>• {s}</li>)}
              </ul>
            </div>
            <div>
              <p className="font-bold text-yellow-400 mb-2">⚡ Areas to Improve</p>
              <ul className="text-slate-300 space-y-1">
                {feedback?.improvements?.map((i, idx) => <li key={idx}>• {i}</li>)}
              </ul>
            </div>
          </div>
          <button
            onClick={() => { setScore(null); setTranscript(''); setFeedback(null); }}
            className="px-6 py-3 bg-slate-600 text-white rounded font-bold hover:bg-slate-500 flex items-center gap-2 mx-auto"
          >
            <RotateCcw size={20} /> Try Again
          </button>
        </div>
      )}
    </div>
  );
}
