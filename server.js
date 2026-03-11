const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const evaluationRoute = require("./routes/evaluation");
const complaintRoute = require("./routes/complaint");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api", evaluationRoute);
app.use("/api", complaintRoute);

mongoose.connect("mongodb://127.0.0.1:27017/sentinelFlow")
.then(()=>console.log("MongoDB Connected"))
.catch(err => console.log(err));

app.listen(5000,()=>{
console.log("Server running on port 5000");
});