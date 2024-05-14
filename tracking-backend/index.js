// DB imports
import { readTrackingEvents, setTrackingEnd, setTrackingStart } from './src/persistence.js';


// Express imports
//const express = require('express');
import express from 'express';
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

app.post('/api/v1/tracking/events/start', async(req, res) => {
    console.log(`\n
    ============
    Received event start:\n
    ${JSON.stringify(req.body)}
    ============
    \n`);
    await setTrackingStart(req.body.orderId, req.body.stationId, new Date(req.body.startTime).getTime());
    res.sendStatus(204);
});

app.post('/api/v1/tracking/events/end', async(req, res) => {
    console.log(`\n
    ============
    Received event end:\n
    ${JSON.stringify(req.body)}
    ============
    \n`);
    await setTrackingEnd(req.body.orderId, req.body.stationId, new Date(req.body.endTime).getTime());
    res.sendStatus(204);
});

app.get('/api/v1/tracking/events/aggregate', async(req, res) => {
    // TODO: Incorrect response for now
    const trackingEvents = await readTrackingEvents();
    console.log("TrackingEvents: ", trackingEvents)
    res.json(trackingEvents).send();
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});