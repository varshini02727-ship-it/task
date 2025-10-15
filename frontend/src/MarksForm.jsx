import React, { useState } from "react";
import axios from "axios";

function MarksForm() {
  const [marks, setMarks] = useState({
    math: "",
    science: "",
    english: "",
    history: "",
    computer: "",
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setMarks({ ...marks, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("access");
      const res = await axios.post("http://127.0.0.1:8000/api/marks/", marks, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setResult(res.data);
    } catch (err) {
      alert("Error submitting marks.");
    }
  };

  return (
    <div>
      <h2>Enter Marks</h2>
      {Object.keys(marks).map((subject) => (
        <div key={subject}>
          <label>{subject}: </label>
          <input
            type="number"
            name={subject}
            value={marks[subject]}
            onChange={handleChange}
          />
        </div>
      ))}
      <button onClick={handleSubmit}>Submit</button>

      {result && (
        <div>
          <h3>Average: {result.average}</h3>
          <h3>Grade: {result.grade}</h3>
        </div>
      )}
    </div>
  );
}

export default MarksForm;
