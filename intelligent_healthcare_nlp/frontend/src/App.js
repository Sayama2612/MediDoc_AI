import React, {useState} from 'react'
import axios from 'axios'

export default function App(){
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [entities, setEntities] = useState(null)
  const [summary, setSummary] = useState('')
  const [prediction, setPrediction] = useState(null)

  const onUpload = async (e) => {
    e.preventDefault()
    if(!file) return alert('select file')
    const fd = new FormData()
    fd.append('file', file)
    const res = await axios.post('/upload', fd)
    setText(res.data.text)
  }

  const runNER = async () => {
    const res = await axios.post('/ner', {text})
    setEntities(res.data.entities)
  }

  const runSumm = async () => {
    const res = await axios.post('/summarize', {text})
    setSummary(res.data.summary)
  }

  const runPredict = async () => {
    const res = await axios.post('/predict', {text})
    setPrediction(res.data)
  }

  return (
    <div style={{padding:20, fontFamily:'Arial'}}>
      <h1>Intelligent Healthcare NLP</h1>

      <section style={{marginTop:20}}>
        <h2>Upload Document</h2>
        <form onSubmit={onUpload}>
          <input type="file" onChange={e=>setFile(e.target.files[0])} />
          <button type="submit">Upload</button>
        </form>
        <pre style={{background:'#f3f3f3', padding:10}}>{text}</pre>
      </section>

      <section style={{marginTop:20}}>
        <h2>Actions</h2>
        <button onClick={runNER}>Extract Entities</button>
        <button onClick={runSumm}>Summarize</button>
        <button onClick={runPredict}>Classify</button>
      </section>

      <section style={{marginTop:20}}>
        <h3>Entities</h3>
        <pre>{entities?JSON.stringify(entities,null,2):'No entities'}</pre>
      </section>

      <section style={{marginTop:20}}>
        <h3>Summary</h3>
        <pre>{summary}</pre>
      </section>

      <section style={{marginTop:20}}>
        <h3>Prediction</h3>
        <pre>{prediction?JSON.stringify(prediction,null,2):'No prediction'}</pre>
      </section>

    </div>
  )
}
