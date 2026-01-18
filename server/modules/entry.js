require('dotenv').config()
const mongoose = require('mongoose')

mongoose.set('strictQuery', false)

const url = process.env.MONGODB_URI

console.log('connecting to', url)
mongoose.connect(url)
  .then(result =>{
    console.log('connected to MongoDB')
  })
  .catch(error =>{
    console.log('error connecting to MongoDB:', error.message)
  })
mongoose.set('strictQuery',false)

const entrySchema = new mongoose.Schema({
  summary: {
    type: String,
  },
  timestamp: {
    type: String,
  },
  videoURL: {
    type:String
  },
  severity: {
    type:Number,
  },
  incidentType: {
    type:String,
  },
})

entrySchema.set('toJSON', {
  transform: (document, returnedObject) => {
    returnedObject.id = returnedObject._id.toString()
    delete returnedObject._id
    delete returnedObject.__v
  }
})

// Helper function to get a model for a specific collection
function getEntryModel(collectionName) {
  // reuse existing model if already compiled
  if (mongoose.models[collectionName]) {
    return mongoose.models[collectionName]
  }
  // otherwise, create a new one bound to that collection
  return mongoose.model('Entry', entrySchema, collectionName)
}

module.exports = { getEntryModel }
//mongoDB setup
