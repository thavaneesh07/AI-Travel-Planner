import React, { useState } from 'react';
import axios from 'axios';

function Chatbot() {
  const [message, setMessage] = useState(''); // This holds what the user types
  const [response, setResponse] = useState(null); // This holds the robot's answer

  const sendMessage = async () => {
    try {
      // Send the message to the backend (like mailing a letter)
      const result = await axios.post('http://localhost:8000/api/parse', { message });
      setResponse(result.data); // Show the robot's parsed answer
    } catch (error) {
      console.error('Oops, error:', error); // If something goes wrong, print it
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Travel Chat Robot</h1>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)} // Update what you type
        placeholder="Type your trip idea, like 'Trip to Paris Oct 1-7, budget 1500'"
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      <button onClick={sendMessage} style={{ padding: '10px 20px' }}>Send</button>
      {response && (
        <div style={{ marginTop: '20px', border: '1px solid black', padding: '10px' }}>
          <h2>Robot Says:</h2>
          <p>Destination: {response.destination}</p>
          <p>Start Date: {response.start_date}</p>
          <p>End Date: {response.end_date}</p>
          <p>Budget: {response.budget}</p>
          <p>Profile: {response.user_profile}</p>
          <p>Interests: {response.interests?.join(', ')}</p>
        </div>
      )}
    </div>
  );
}

export default Chatbot;