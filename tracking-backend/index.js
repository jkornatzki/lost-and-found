const express = require('express');
const app = express();

const port = 3000;


app.use(express.json());

app.post('/api/v1/station/check', (req, res) => {
    // For "unsuccessful ID" send unsuccessful event
    if(req.body.orderId === 'B_2663588') {
        res.send({
            "isAtCorrectStation": false,
            "expectedStation": 2
        });
    } else {
        res.send({
            "isAtCorrectStation": true,
            "expectedStation": 1
        });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});