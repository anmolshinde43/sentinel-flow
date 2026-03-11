const express = require("express");
const router = express.Router();
const Complaint = require("../models/Complaint");

/* GET complaints */

router.get("/complaints", async (req, res) => {
  const complaints = await Complaint.find();
  res.json(complaints);
});

/* SAVE complaint */

router.post("/complaints", async (req, res) => {

  const newComplaint = new Complaint(req.body);

  await newComplaint.save();

  res.json(newComplaint);

});

router.delete("/complaints/:id", async (req, res) => {

  await Complaint.findByIdAndDelete(req.params.id);

  res.json({ message: "Complaint deleted" });

});

module.exports = router;