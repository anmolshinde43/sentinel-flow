const mongoose = require("mongoose");

const ComplaintSchema = new mongoose.Schema({
  name: String,
  against: String,
  type: String,
  priority: String,
  description: String,
  status: String
});

module.exports = mongoose.model("Complaint", ComplaintSchema);