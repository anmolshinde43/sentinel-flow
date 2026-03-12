import React, { useState } from "react";

function EvaluationForm({ evaluations, setEvaluations }) {

  const [name, setName] = useState("");
  const [employeeType, setEmployeeType] = useState("");
  const [skills, setSkills] = useState("");
  const [workstyle, setWorkstyle] = useState("");
  const [search, setSearch] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const avg = (Number(skills) + Number(workstyle)) / 2;

    let decision = "";
    let reason = "";

    if (avg >= 7) {
      decision = "Confirm";
      reason = "Strong performance and work discipline";
    } 
    else if (avg >= 5) {
      decision = "Extend";
      reason = "Average performance, improvement required";
    } 
    else {
      decision = "Terminate";
      reason = "Low performance and poor work style";
    }

    const newEvaluation = {
      name,
      employeeType,
      skills,
      workstyle,
      decision,
      reason
    };

    const res = await fetch("http://localhost:5000/api/evaluations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(newEvaluation)
    });

    const data = await res.json();

    setEvaluations([...evaluations, data]);

    setName("");
    setEmployeeType("");
    setSkills("");
    setWorkstyle("");
  };

  const deleteEvaluation = async (id) => {

  await fetch(`http://localhost:5000/api/evaluations/${id}`, {
    method: "DELETE"
  });

  setEvaluations(evaluations.filter(e => e._id !== id));

};

  return (
    <div className="panel">

      <h3>Employee Evaluation</h3>

      <form onSubmit={handleSubmit}>

        <input
          placeholder="Employee Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <select
  value={employeeType}
  onChange={(e) => setEmployeeType(e.target.value)}
  required
>
  <option value="">Select Employee Type</option>
  <option value="Employee">Employee</option>
  <option value="Intern">Intern</option>
  <option value="Contract">Contract Worker</option>
</select>

        <input
          type="number"
          placeholder="Skill Score (0-10)"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Work Style Score (0-10)"
          value={workstyle}
          onChange={(e) => setWorkstyle(e.target.value)}
          required
        />

        <button type="submit">Evaluate</button>

      </form>

      <h3>Evaluation Records</h3>

      <input
        placeholder="Search Employee"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <table>

        <thead>
          <tr>
            <th>Employee</th>
            <th>Type</th>
            <th>Skills</th>
            <th>Work Style</th>
            <th>Decision</th>
            <th>AI Reason</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>

          {evaluations
            .filter((e) =>
              e.name.toLowerCase().includes(search.toLowerCase())
            )
            .map((e) => (

              <tr key={e._id}>

                <td>{e.name}</td>
                <td>{e.employeeType}</td>
                <td>{e.skills}</td>
                <td>{e.workstyle}</td>

                <td>
                  <span className={`badge ${e.decision.toLowerCase()}`}>
                    {e.decision}
                  </span>
                </td>

                <td>{e.reason}</td>

                <td>
                  <button onClick={() => deleteEvaluation(e._id)}>
                    Delete
                  </button>
                </td>

              </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}

export default EvaluationForm;