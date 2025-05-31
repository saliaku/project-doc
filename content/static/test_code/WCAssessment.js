import React, { useState, useEffect } from 'react';
const importAll = (r) => r.keys().map(r);

// Import images and audio files
const rawImages = importAll(require.context('../media/images', false, /\.(jpeg|jpg|png|gif)$/));
const rawAudio = importAll(require.context('../media/audio', false, /\.(mp4|wav|ogg)$/));

// Image and audio mapping logic
const imageMapping = [
  { range: [1, 3], alt: 'triangle' },
  { range: [4, 6], alt: 'square' },
  { range: [7, 9], alt: 'circle' }
];

const audioMapping = [
  { range: [1, 3], alt: 'cycle' },
  { range: [4, 6], alt: 'car' },
  { range: [7, 9], alt: 'bike' },
];

// Function to get the correct alt text based on index and mapping
const getAltText = (index, mapping) => {
  for (let map of mapping) {
    if (index + 1 >= map.range[0] && index + 1 <= map.range[1]) {
      return map.alt;
    }
  }
  return 'unknown';
};

// Map images with correct alt texts
const visuals = rawImages.map((src, index) => {
  const alt = getAltText(index, imageMapping);
  return {
    id: index + 1,
    type: 'image',
    alt,
    src,
  };
});

// Map audio clips with correct alt texts
const audioClips = rawAudio.map((src, index) => {
  const alt = getAltText(index, audioMapping);
  return {
    id: index + 1,
    type: 'audio',
    alt,
    src,
  };
});

const words = [
  { id: 1, type: 'word', text: 'Apple', alt: 'Apple' },
  { id: 2, type: 'word', text: 'Banana', alt: 'Banana' },
  { id: 3, type: 'word', text: 'Cherry', alt: 'Cherry' },
  { id: 4, type: 'word', text: 'Kiwi', alt: 'Kiwi' },
  { id: 5, type: 'word', text: 'APPLE', alt: 'Apple' },
  { id: 6, type: 'word', text: 'BANANA', alt: 'Banana' },
  { id: 7, type: 'word', text: 'CHERRY', alt: 'Cherry' },
  { id: 8, type: 'word', text: 'KIWI', alt: 'Kiwi' },
  { id: 9, type: 'word', text: 'apple', alt: 'Apple' },
  { id: 10, type: 'word', text: 'banana', alt: 'Banana' },
  { id: 11, type: 'word', text: 'cherry', alt: 'Cherry' },
  { id: 12, type: 'word', text: 'kiwi', alt: 'Kiwi' },
];

// Function to shuffle an array and limit the number of items
const shuffleArray = (array, limit = 7) => {
  return array.sort(() => Math.random() - 0.5).slice(0, limit);
};

const WMCAssessment = ({ updateScoresWMC }) => {
  const [currentTest, setCurrentTest] = useState('image'); // 'image', 'audio', 'text'
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [sectionScore, setSectionScore] = useState({ image: 0, audio: 0, text: 0 });
  const [items, setItems] = useState([]);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    // Initialize items based on the current test type and shuffle them
    let initialItems = [];
    switch (currentTest) {
      case 'image':
        initialItems = shuffleArray([...visuals], 7);
        break;
      case 'audio':
        initialItems = shuffleArray([...audioClips], 7);
        break;
      case 'text':
        initialItems = shuffleArray([...words], 7);
        break;
      default:
        initialItems = [];
    }
    setItems(initialItems);
  }, [currentTest]);

  const handleAnswer = (answer) => {
    if (currentIndex >= 2) {
      const isSameAsTwoBack = items[currentIndex]?.alt === items[currentIndex - 2]?.alt;
      if (answer === isSameAsTwoBack) {
        setScore((prev) => prev + 1);
        setSectionScore((prevScores) => {
          const updatedScores = {
            ...prevScores,
            [currentTest]: prevScores[currentTest] + 1,
          };
          updateScoresWMC(updatedScores); // Pass the updated scores
          return updatedScores;
        });
      }
    }
    if (currentIndex < items.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      // Proceed to the next test or end the assessment
      if (currentTest === 'image') {
        setCurrentTest('audio');
      } else if (currentTest === 'audio') {
        setCurrentTest('text');
      } else {
        setIsCompleted(true); // Mark the test as completed
      }
      setCurrentIndex(0); // Reset index for the next test
    }
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
      <h1 className="text-2xl font-bold mb-4">Working Memory Capacity Assessment</h1>
      <h2 className="text-xl font-semibold mb-4">
        Current Test: {currentTest.charAt(0).toUpperCase() + currentTest.slice(1)}
      </h2>

      {/* Dynamic Instructions */}
      <p className="mb-2 text-gray-700">
        {currentTest === 'image' && 
          'Observe each image carefully. If you believe the current shape is the same as the one shown two items ago, select "Yes". Otherwise, select "No". You may IGNORE the colour of the shape.'}
        {currentTest === 'audio' && 
          'Listen to each audio clip attentively. If you think the current vehicle matches the one played two items ago, select "Yes". Otherwise, select "No". You may IGNORE the voice. The audio clip can be played multiple times.'}
        {currentTest === 'text' && 
          'Read each word displayed on the screen. If the current fruit matches the one displayed two items ago, select "Yes". Otherwise, select "No". You may IGNORE the casing of the words.'}
      </p>

      {/* Current Test Content */}
      <div className="mb-4">
        {currentTest === 'image' && items[currentIndex]?.type === 'image' && (
          <img
            src={items[currentIndex].src}
            alt={items[currentIndex].alt}
            style={{ width: '300px', height: '300px', objectFit: 'cover' }}
            className="mb-2"
          />
        )}
        {currentTest === 'audio' && items[currentIndex]?.type === 'audio' && (
          <audio
            key={items[currentIndex].id}
            controls
            className="mb-2"
          >
            <source src={items[currentIndex].src} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        )}
        {currentTest === 'text' && items[currentIndex]?.type === 'word' && (
          <p className="text-xl font-semibold">{items[currentIndex].text}</p>
        )}
      </div>

      {/* Answer Section */}
      {currentIndex >= 2 && (
        <div>
          <p className="text-lg mb-4">Is this the same content shown 2 items ago?</p>
          <div className="flex justify-around">
            <button
              onClick={() => handleAnswer(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition duration-200"
            >
              Yes
            </button>
            <button
              onClick={() => handleAnswer(false)}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition duration-200"
            >
              No
            </button>
          </div>
        </div>
      )}

      {currentIndex < 2 && (
        <button
          onClick={() => setCurrentIndex((prev) => prev + 1)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
        >
          Next
        </button>
      )}
    </div>
  );
};

export default WMCAssessment;
