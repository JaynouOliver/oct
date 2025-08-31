'use client';

import { useState } from 'react';

interface QueryResponse {
  question: string;
  restructured_question: string;
  answer: string;
  context: string[];
}

const demoQuestions = [
  "What is the main topic of this research paper?",
  "What are the key findings about tax filing?",
  "What models were compared in the experiments?",
  "What is the SARA dataset?",
  "How does the neuro-symbolic approach work?",
  "What are the results for the Baseline model family?",
  "Which model has the lowest break-even price?",
  "what is there is figure 1"
];

export default function Home() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [restructuredQuestion, setRestructuredQuestion] = useState('');
  const [context, setContext] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(3);

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          top_k: topK
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data: QueryResponse = await response.json();
      setAnswer(data.answer);
      setRestructuredQuestion(data.restructured_question);
      setContext(data.context);
    } catch (error) {
      console.error('Error:', error);
      setAnswer('Sorry, there was an error processing your question.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoQuestion = (demoQ: string) => {
    setQuestion(demoQ);
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-black mb-2">
            🤖 Document Q&A System
          </h1>
          <p className="text-lg text-black">
            Ask questions about the financial reasoning research paper using AI-powered search
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Demo Questions */}
          <div className="bg-white border border-gray-300 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-black">💡 Try These Questions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {demoQuestions.map((demoQ, index) => (
                <button
                  key={index}
                  onClick={() => handleDemoQuestion(demoQ)}
                  className="text-left p-3 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg transition-colors text-sm text-black"
                >
                  {demoQ}
                </button>
              ))}
            </div>
          </div>

          {/* Query Section */}
          <div className="bg-white border border-gray-300 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-black">💬 Ask a Question</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Question
                </label>
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g., What is the main topic of this research paper?"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Number of context chunks: {topK}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={handleQuery}
                disabled={loading || !question.trim()}
                className="w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-colors"
              >
                {loading ? '🔍 Searching...' : '🔍 Ask Question'}
              </button>
            </div>
          </div>

          {/* Restructured Question Section */}
          {restructuredQuestion && restructuredQuestion !== question && (
            <div className="bg-white border border-gray-300 rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4 text-black">🔄 Query Restructured</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Original: <span className="italic">{question}</span></p>
                <p className="text-black font-medium">Restructured: {restructuredQuestion}</p>
              </div>
            </div>
          )}

          {/* Answer Section */}
          {answer && (
            <div className="bg-white border border-gray-300 rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4 text-black">🤖 Answer</h2>
              <div className="prose max-w-none">
                <p className="text-black leading-relaxed">{answer}</p>
              </div>
            </div>
          )}

          {/* Context Section */}
          {context.length > 0 && (
            <div className="bg-white border border-gray-300 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-black">📖 Context Sources</h2>
              <div className="space-y-4">
                {context.map((ctx, index) => (
                  <div key={index} className="border-l-4 border-black pl-4">
                    <h3 className="font-medium text-black mb-2">Source {index + 1}</h3>
                    <p className="text-black text-sm">
                      {ctx.length > 500 ? `${ctx.substring(0, 500)}...` : ctx}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-black">
          Powered by ChromaDB Cloud + OpenAI | Built with Next.js
        </div>
      </div>
    </div>
  );
}
