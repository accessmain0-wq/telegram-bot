const express = require("express");
const { exec } = require("child_process");
const multer = require("multer");

const app = express();
const upload = multer({ dest: "bots/" });

app.use(express.static("public"));

// upload bot
app.post("/upload", upload.single("bot"), (req, res) => {
    res.send("Uploaded: " + req.file.filename);
});

// start bot
app.get("/start/:file", (req, res) => {
    exec(`php bots/${req.params.file}`);
    res.send("Bot Started");
});

// stop bot
app.get("/stop", (req, res) => {
    exec("pkill php");
    res.send("Stopped");
});

app.listen(10000, () => console.log("Server running"));
