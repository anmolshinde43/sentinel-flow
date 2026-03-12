const express = require("express");
const router = express.Router();
const Evaluation = require("../models/Evaluation");

/* GET all evaluations */

router.get("/evaluations", async (req, res) => {
  const evaluations = await Evaluation.find();
  res.json(evaluations);
});
/* SAVE evaluation */

router.post("/evaluations", async (req, res) => {

  const newEvaluation = new Evaluation(req.body);

  await newEvaluation.save();

  res.json(newEvaluation);

});

router.delete("/evaluations/:id", async (req, res) => {

  try {

    await Evaluation.findByIdAndDelete(req.params.id);

    res.json({ message: "Evaluation deleted successfully" });

  } catch (error) {

    res.status(500).json(error);

  }

});

module.exports = router;