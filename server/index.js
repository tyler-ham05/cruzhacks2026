const express = require('express')
const morgan = require('morgan')
const cors = require('cors')
const app = express()
const {getEntryModel } = require('./modules/entry')
require('dotenv').config()

morgan.token('body', (req) => {
  return req.method === 'POST' ? JSON.stringify(req.body) : ''
})

const errorHandler = (error, request, response, next) => {
  console.error(error.message)

  if (error.name === 'CastError') {
    return response.status(400).send({ error: 'malformatted id' })
  }
  else if (error.name == 'ValidationError'){
    return response.status(400).json({error: error.message})
  } 

  next(error)
}

app.use(express.json())
app.use(morgan(':method :url :status :res[content-length] :response-time ms :body'))
app.use(express.static('dist'))
app.use(cors())

console.log('hello world')
//api calls go here

app.get('/', async (req, res) => {
  res.json("hello world")
})

app.get('/api/:userID', async (req, res) => {
  try {
    const { userID } = req.params
    const EntryModel = getEntryModel(userID)
    const entries = await EntryModel.find({})
    res.json(entries)
  } catch (error) {
    next(error)
  }
})

app.post('/api', async (req, res, next) => {
    const user = req.body.userID
    const EntryModel = getEntryModel(user)
    const body = req.body
    const entry = new EntryModel({
        summary: body.summary,
        timestamp: body.timestamp,
        videoURL: body.videoURL,
        severity: body.severity,
        incidentType: body.incidentType
    })
    entry.save()
    .then(savedEntry => {
    res.status(201).json(savedEntry)
  })
    .catch(error => next(error))
})

//api calls end here
app.use(errorHandler)

const PORT = process.env.PORT
/*
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
*/
module.exports = app