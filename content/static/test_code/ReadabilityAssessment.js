import React, { useState } from 'react';

const ReadabilityAssessment = ({ updateScores }) => {
  const [text, setText] = useState('');
  const [score, setScore] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const calculateReadability = (text) => {
    const words = text.split(/\s+/).filter(word => word.length > 0).length;
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0).length;
    const syllables = text.split(/\s+/).reduce((count, word) => count + countSyllables(word), 0);

    // Handle edge cases: prevent division by zero
    if (words === 0 || sentences === 0) return 0;

    // Flesch Reading Ease formula
    const fleschScore = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words));
    return Math.max(0, Math.min(100, Math.round(fleschScore))); // Limit score between 0 and 100
  };

  const countSyllables = (word) => {
    word = word.toLowerCase();
    if (word.length <= 3) return 1;
    const syllablePattern = /[aeiouy]+/g;
    const matches = word.match(syllablePattern) || [];
    
    // Adjust syllable count for specific cases, e.g., silent 'e'
    let syllables = matches.length;
    if (word.endsWith("e") && syllables > 1) syllables -= 1; // Silent 'e' at end of word
    return syllables;
  };


  const handleSubmit = (event) => {
    event.preventDefault();
    if (text.trim() === '') {
      alert('Please write something before submitting.');
      return;
    }
    const readabilityScore = calculateReadability(text);
    setScore(readabilityScore);
    updateScores(readabilityScore); // Update the parent component's score
    setIsCompleted(true); // Set the completion state
  };

  if (isCompleted) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-2xl font-bold">This Section Completed</h1>
        <p className="text-xl mt-4">Go on to the next test below</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-2xl font-bold mb-4">Readability Assessment</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows="8"
          className="w-full p-2 border rounded-lg shadow"
          placeholder="Write about your school in 4-5 sentences."
        ></textarea>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-semibold py-2 rounded hover:bg-blue-600 transition duration-200"
        >
          Submit
        </button>
      </form>

      {/* {score !== null && (
        <div className="mt-4">
          <h2 className="text-xl font-semibold">Readability Score: {score}</h2>
        
        </div>
      )} */}
    </div>
  );
};

export default ReadabilityAssessment;
