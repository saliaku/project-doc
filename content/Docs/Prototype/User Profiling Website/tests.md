---
title: Assessments implementation
cascade:
type: default
weight: 4
---

## Readability Assessment

```js

// --------> component setup & state management 
import React, { useState } from 'react';

const ReadabilityAssessment = ({ updateScores }) => {
  const [text, setText] = useState('');
  const [score, setScore] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);

 // --------> readability score calculation
  const calculateReadability = (text) => {
    const words = text.split(/\s+/).filter(word => word.length > 0).length;
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0).length;
    const syllables = text.split(/\s+/).reduce((count, word) => count + countSyllables(word), 0);

    // Handle edge cases: prevent division by zero
    if (words === 0 || sentences === 0) return 0;

    // Flesch Reading Ease formula implemented here
    const fleschScore = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words));
    return Math.max(0, Math.min(100, Math.round(fleschScore))); // Limit score between 0 and 100
  };

// --------> syllable counting 
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

// --------> form submit handler
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

// --------> conditional rendering after submission
  if (isCompleted) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-2xl font-bold">This Section Completed</h1>
        <p className="text-xl mt-4">Go on to the next test below</p>
      </div>
    );
  }
// --------> the Main return - Assessment form 
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

    </div>
  );
};

export default ReadabilityAssessment;

```

 Download [ReadabilityAssessment.js](/static/test_code/ReadabilityAssessment.js) from here.





## Working Memory Capacity Assessment

```js

//--------> import dependencies & assets

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

//-------->  handle user answer
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

  //-------->  render the assessment
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

```

 Download [WMCAssessment.js](/static/test_code/WCAssessment.js) from here.

## Information Processing Assessment

```js
import React, { useState } from "react";
import testimage from "../media/ip_test_material/visual_test.jpeg"; // Replace with your actual image path
import testaudio from "../media/ip_test_material/audio_test.mp4"; // Replace with your actual audio path
import queimage from "../media/ip_test_material/option3.jpg"; 

// --------------> textual, visual & auditory content along with the questions & answer

const textRecap = `
The water cycle is how water moves around the Earth. It starts when the Sun heats water in oceans, lakes, and rivers, turning it into vapor, which rises into the sky. This is called evaporation. The water vapor cools and forms clouds, a process called condensation. When the clouds get heavy, water falls back to the Earth as rain, snow, or hail—this is called precipitation. The water then flows back into rivers and oceans, ready to start the cycle again. This process helps keep plants, animals, and people alive.`;

const textQuestions = [
  {
    question: "What is the process called when water turns into vapor and rises into the sky?",
    options: ["Precipitation", "Evaporation", "Condensation", "Freezing"],
    correctAnswer: "Evaporation",
  },
  {
    question: 'Why do clouds form in the sky?',
    options: [
      "Water vapor cools and turns into clouds",
      "The Sun heats the clouds",
      "Rain falls and creates clouds",
      " Clouds rise from the ground",
    ],
    correctAnswer: "Water vapor cools and turns into clouds",
  },
  {
    question:
      "On a very sunny day, which part of the water cycle is likely to happen faster?",
    options: [
      " Condensation",
      "Evaporation",
      "Precipitation",
      "Freezing",
    ],
    correctAnswer: "Evaporation",
  },
  {
    question: "What could happen to plants if there was no precipitation for a long time?",
    options: [
      "Plants would grow taller",
      "Plants would dry out and may die",
      " Plants would have extra water",
      "Plants would turn into clouds",
    ],
    correctAnswer:
      "Plants would dry out and may die",
  },
  {
    question:
      "Why is the water cycle important for life on Earth?",
    options: [" It creates electricity", "It keeps water clean and flowing for plants, animals, and people", "It makes the Sun shine brighter", "It helps clouds stay in the sky"],
    correctAnswer: "It keeps water clean and flowing for plants, animals, and people",
  },
  {
    question: "If you were to write a story about the water cycle, what would be the best way to start?",
    options: [
      "Describe a raindrop falling from a cloud",
      "Begin with a water droplet in the ocean",
      "Show plants using water to grow",
      "Introduce a river flowing to the ocean",
    ],
    correctAnswer: "Begin with a water droplet in the ocean",
  },
];

const visualRecap = `
Look carefully at the image provided and answer the questions based on your memory of it.
`;

const visualQuestions = [
  {
    question: "Which is the correct order of shapes in the image?",
    options: [
      "Circle, square, rectangle",
      "Triangle, circle, square",
      "Square, circle, triangle",
      "Rectangle, triangle, circle",
    ],
    correctAnswer: "Square, circle, triangle",
  },

  {
    question: "What geometric property does the square have?",
    options: ["All sides are equal", "No sides are equal", "It has no straight lines", "It has only one side"],
    correctAnswer: "All sides are equal",
  },

  {
    question: "Is Square a Rectangle?",
    options: [
      "Yes",
      "No",
    ],
    correctAnswer: "Yes",
  },
  {
    question: "Which shapes are symmetrical? (Symmetry means if you fold a shape along a line, both sides will match perfectly.)",
    options: [
      "Circle and triangle",
      "Square and circle",
      "Only the square",
      "All shapes",
    ],
    correctAnswer: "All shapes",
  },

  {
    question: " Which shape would be the most difficult to draw freehand?",
    options: ["square", "triangle", "circle", "All"],
    correctAnswer: "circle",
  },

  {
    question: 'Can this image be created using the shapes given ?',
    options: ['Yes', 'No'],
    correctAnswer: 'No', // Assuming the image shows a square, circle, and triangle
    image: queimage, // Path to the image generated or created from shapes
  },

  // Add other visual questions here...
];

const auditoryRecap = `
Listen carefully to the audio clip and answer the questions based on what you remember hearing.
`;

const auditoryQuestions = [
  {
    question: "What was the second sound in the audio clip?",
    options: [
      "A car honking",
      "A high-pitched bell",
      "Thunder",
      "Birds chirping",
    ],
    correctAnswer: "Thunder",
  },

  {
    question: "What does the sound of a car honking typically indicate?",
    options: [
      "A warning or attention",
      "A relaxing atmosphere",
      " The start of a storm",
      "A bird is nearby",
    ],
    correctAnswer: "A warning or attention",
  },

  {
    question:
      "If you wanted to simulate an incoming storm in a soundscape, which of these sounds would you focus on?",
    options: [
      "A car honking",
      "A high-pitched bell",
      "Thunder",
      "Birds chirping",
    ],
    correctAnswer: "Thunder",
  },

  {
    question:
      'Which two sounds in the sequence can be categorized as "natural"',
    options: [
      "Car honking and high-pitched bell",
      " Thunder and birds chirping",
      "High-pitched bell and birds chirping",
      "Thunder and car honking",
    ],
    correctAnswer: " Thunder and birds chirping",
  },

  {
    question:
      "You are designing an alarm system for use during a thunderstorm. Which sound would be the least reliable for alerting people during the storm?",
    options: [
      "A car honking",
      "A high-pitched bell",
      "Thunder",
      "Birds chirping",
    ],
    correctAnswer: "Thunder",
  },

  {
    question:
      " How would you use the sounds to enhance a storytelling scene about a peaceful morning turning into chaos?",
    options: [
      "Birds chirping → Car honking → Thunder",
      "Car honking → Birds chirping → Thunder",
      "Thunder → High-pitched bell → Birds chirping",
      "Thunder → High-pitched bell → Car honking",
    ],
    correctAnswer: "Birds chirping → Car honking → Thunder",
  },
  // Add other auditory questions here...
];

const IPAssessment = ({ updateScoresIP }) => {
  const [currentStep, setCurrentStep] = useState("intro");
  const [currentSection, setCurrentSection] = useState("text");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [sectionScore, setSectionScore] = useState({
    text: 0,
    image: 0,
    audio: 0,
  });

  const startSection = (section) => {
    setCurrentSection(section);
    setCurrentQuestionIndex(0);
    setCurrentStep("recap");
  };

  const handleAnswerSelect = (selectedOption) => {
    const currentQuestions = getCurrentQuestions();
    
    if (currentQuestions && currentQuestionIndex < currentQuestions.length) {
      const isCorrect = 
        selectedOption === currentQuestions[currentQuestionIndex].correctAnswer;
      
      if (isCorrect) {
        // Increment the section-specific score and update IP scores
        setSectionScore((prevSectionScore) => {
          const updatedScores = {
            ...prevSectionScore,
            [currentSection]: prevSectionScore[currentSection] + 1,
          };
          // Update the overall score in parent component
          updateScoresIP(updatedScores);
          return updatedScores;
        });
  
        // Increment the total score
        setScore((prevScore) => prevScore + 1);
      }
  
      // Check if there are more questions in the current section
      if (currentQuestionIndex < currentQuestions.length - 1) {
        setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
      } else {
        // Move to the next section or show results
        if (currentSection === "text") {
          startSection("image");
        } else if (currentSection === "image") {
          startSection("audio");
        } else {
          setCurrentStep("results");
        }
      }
    }
  };
  
//---------> section based question rendered
  const getCurrentQuestions = () => {
    switch (currentSection) {
      case "text":
        return textQuestions;
      case "image":
        return visualQuestions;
      case "audio":
        return auditoryQuestions;
      default:
        return [];
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white shadow-lg rounded-lg p-6 max-w-md w-full">
        {currentStep === "intro" && (
          <div>
            <h2 className="text-lg font-bold mb-4">General Instructions</h2>
            <div className="mb-4">
              This test will assess your ability to process information across three sections:{" "}
              <strong>Text, Visual, and Auditory</strong>. Each section includes
              multiple-choice questions (MCQs) based on the provided content.
              Follow these instructions for a successful attempt:
              <ul className="list-disc pl-5 mt-2 mb-4">
                <li>
                  Read the text or observe/listen carefully before answering the
                  given set of questions.
                </li>
                <li>
                  Each question has four options, and you need to select the one
                  you believe is correct.
                </li>
                <li>Click on your answer to proceed to the next question.</li>
                <li>
                  Try to stay focused and avoid distractions to maximize your
                  recall ability.
                </li>
              </ul>
              Take your time and do your best—good luck!
            </div>
            <button
              onClick={() => startSection("text")}
              className="bg-blue-500 text-white font-semibold py-2 px-4 rounded shadow hover:bg-blue-600 transition duration-200"
            >
              Next
            </button>
          </div>
        )}

        {currentStep === "recap" && (
          <div>
            <h2 className="text-lg font-bold mb-4">
              {currentSection === "text"
                ? "Read the below passage carefully"
                : currentSection === "image"
                ? "Visual Test"
                : "Auditory Test"}
            </h2>
            <p className="mb-4">
              {currentSection === "text"
                ? textRecap
                : currentSection === "image"
                ? visualRecap
                : auditoryRecap}
            </p>
            {currentSection === "image" && (
              <img
                src={testimage}
                alt="Visual Memory Test"
                className="w-full mb-4"
              />
            )}
            {currentSection === "audio" && (
              <audio controls className="w-full mb-4">
                <source src={testaudio} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            )}
            <button
              onClick={() => setCurrentStep("questions")}
              className="bg-blue-500 text-white font-semibold py-2 px-4 rounded shadow hover:bg-blue-600 transition duration-200"
            >
              Start Quiz
              {/* {currentSection.charAt(0).toUpperCase() + currentSection.slice(1)} */}
            </button>
          </div>
        )}

        {currentStep === "questions" && (
          <div>
            {getCurrentQuestions()[currentQuestionIndex] ? (
              <>
                <h2 className="text-lg font-bold mb-4">
                  Question {currentQuestionIndex + 1}
                </h2>
                <p className="mb-4">
                  {getCurrentQuestions()[currentQuestionIndex].question}
                </p>
                <div>
                {getCurrentQuestions()[currentQuestionIndex].image&& (
                  <img
                  src={getCurrentQuestions()[currentQuestionIndex].image}
                  alt="Question related visual"
                  className="mb-4"
                />
                  )}
                </div>
                <div>
                  {getCurrentQuestions()[currentQuestionIndex].options.map(
                    (option, index) => (
                      <button
                        key={index}
                        onClick={() => handleAnswerSelect(option)}
                        className="block w-full bg-blue-500 text-white font-semibold py-2 px-4 rounded shadow mb-2 hover:bg-blue-600 transition duration-200"
                      >
                        {option}
                      </button>
                    )
                  )}
                </div>
              </>
            ) : (
              <p className="text-red-500">
                Error loading question. Please try again.
              </p>
            )}
          </div>
        )}

        {currentStep === "results" && (
          // <div className="text-center">
          <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg text-center">
          <h1 className="text-2xl font-bold">This Section Completed</h1>
          <p className="text-xl mt-4">You may submit the form if all sections are complete.</p>
        
          </div>
        )}
      </div>
    </div>
  );
};

export default IPAssessment;

```

 Download [IPAssessment.js](/static/test_code/IPAssessment.js) from here.