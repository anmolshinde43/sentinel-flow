const mongoose = require("mongoose");

const EvaluationSchema = new mongoose.Schema({
  name: String,
  employeeType: String,
  skills: Number,
  workstyle: Number,
  decision: String,
  reason: String
});

module.exports = mongoose.model("Evaluation", EvaluationSchema);