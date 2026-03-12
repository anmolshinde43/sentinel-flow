import React, { useState, useEffect } from "react";

function ComplaintForm({ complaints, setComplaints }) {

  const [name, setName] = useState("");
  const [against, setAgainst] = useState("");
  const [type, setType] = useState("");
  const [priority, setPriority] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("Open");

  useEffect(() => {
    fetch("http://localhost:5000/api/complaints")
      .then(res => res.json())
      .then(data => setComplaints(data));
  }, [setComplaints]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newComplaint = {
      name,
      against,
      type,
      priority,
      description,
      status
    };

    const res = await fetch("http://localhost:5000/api/complaints", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(newComplaint)
    });

    const data = await res.json();

    setComplaints([...complaints, data]);

    setName("");
    setAgainst("");
    setType("");
    setPriority("");
    setDescription("");
    setStatus("Open");
  };

  // DELETE COMPLAINT
  const deleteComplaint = async (id) => {

    await fetch(`http://localhost:5000/api/complaints/${id}`, {
      method: "DELETE"
    });

    setComplaints(complaints.filter(c => c._id !== id));
  };

  return (
    <div className="panel">

      <h3>Complaint Registration</h3>

      <form onSubmit={handleSubmit}>

        <input
          placeholder="Employee Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          placeholder="Complaint Against"
          value={against}
          onChange={(e) => setAgainst(e.target.value)}
          required
        />

        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          required
        >
          <option value="">Complaint Type</option>
          <option value="Workload Issue">Workload Issue</option>
          <option value="Manager Behaviour">Manager Behaviour</option>
          <option value="Harassment">Harassment</option>
          <option value="Salary Issue">Salary Issue</option>
          <option value="Other">Other</option>
        </select>

        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          required
        >
          <option value="">Priority</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>

        <textarea
          placeholder="Complaint Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="Open">Open</option>
          <option value="Under Review">Under Review</option>
          <option value="Resolved">Resolved</option>
        </select>

        <button type="submit">Submit Complaint</button>

      </form>

      <h3>Complaints List</h3>

      <table>

        <thead>
          <tr>
            <th>Employee</th>
            <th>Against</th>
            <th>Type</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>

          {complaints.map((c) => (

            <tr key={c._id}>

              <td>{c.name}</td>
              <td>{c.against}</td>
              <td>{c.type}</td>
              <td>{c.priority}</td>
              <td>{c.status}</td>
              <td>{c.description}</td>

              <td>
                <button onClick={() => deleteComplaint(c._id)}>
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

export default ComplaintForm;