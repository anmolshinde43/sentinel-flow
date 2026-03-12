import React, { useState, useEffect } from "react";
import EvaluationForm from "./EvaluationForm";
import ComplaintForm from "./ComplaintForm";
import "./App.css";

function App() {

  const [evaluations, setEvaluations] = useState([]);
  const [complaints, setComplaints] = useState([]);

  // Load evaluations from backend
  useEffect(() => {
    fetch("http://localhost:5000/api/evaluations")
      .then(res => res.json())
      .then(data => setEvaluations(data))
      .catch(err => console.log(err));
  }, []);

  // Load complaints from backend
  useEffect(() => {
    fetch("http://localhost:5000/api/complaints")
      .then(res => res.json())
      .then(data => setComplaints(data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div className="container">

      <h1>Sentinel Flow – Workforce Evaluation System</h1>

      {/* Dashboard */}
      <div className="dashboard">

        <div className="card">
          <h3>Total Employees</h3>
          <span>{evaluations.length}</span>
        </div>

        <div className="card">
          <h3>Evaluations</h3>
          <span>{evaluations.length}</span>
        </div>

        <div className="card">
          <h3>Complaints</h3>
          <span>{complaints.length}</span>
        </div>

      </div>

      {/* Evaluation Section */}
      <EvaluationForm
        evaluations={evaluations}
        setEvaluations={setEvaluations}
      />

      {/* Complaint Section */}
      <ComplaintForm
        complaints={complaints}
        setComplaints={setComplaints}
      />

    </div>
  );
}

export default App;