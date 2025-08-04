
import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Container, Typography, Box, Button, Input, Paper, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';


function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [pdfResult, setPdfResult] = useState<any>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const [question, setQuestion] = useState('');
  const [bedrockAnswer, setBedrockAnswer] = useState<string | null>(null);
  const [bedrockLoading, setBedrockLoading] = useState(false);
  const [bedrockError, setBedrockError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setFileName(event.target.files[0].name);
      setPdfResult(null);
      setPdfError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setPdfLoading(true);
    setPdfError(null);
    setPdfResult(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      const response = await fetch('/api/parse-pdf', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to parse PDF');
      }
      const data = await response.json();
      setPdfResult(data);
    } catch (err: any) {
      setPdfError(err.message);
    } finally {
      setPdfLoading(false);
    }
  };

  const handleAskBedrock = async () => {
    if (!question.trim()) return;
    setBedrockLoading(true);
    setBedrockError(null);
    setBedrockAnswer(null);
    try {
      const response = await fetch('/api/ask-bedrock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to get answer');
      }
      const data = await response.json();
      setBedrockAnswer(data.bedrock_response || JSON.stringify(data));
    } catch (err: any) {
      setBedrockError(err.message);
    } finally {
      setBedrockLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h2" component="h1" gutterBottom>
          MindBoost AI: An Intelligent Study Companion
        </Typography>
        <Typography className="subtitle" variant="h5" component="h2" gutterBottom>
          Personalized Learning with Concept Graphs & Burnout Prevention
        </Typography>
      </header>
      <Container maxWidth="sm">
        {/* Section 1: Upload Materials */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Upload your study materials</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Paper elevation={3} className="upload-section" style={{ width: '100%' }}>
              <Box display="flex" flexDirection="column" alignItems="center">
                <label htmlFor="file-upload">
                  <Input
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  <Button variant="contained" color="primary" component="span">
                    Choose File
                  </Button>
                </label>
                {fileName && (
                  <Typography variant="body2" style={{ marginTop: 12, color: '#29335C' }}>
                    Selected: {fileName}
                  </Typography>
                )}
                <Button
                  variant="contained"
                  color="secondary"
                  style={{ marginTop: 16 }}
                  onClick={handleUpload}
                  disabled={!selectedFile || pdfLoading}
                >
                  {pdfLoading ? 'Uploading...' : 'Upload & Parse'}
                </Button>
                {pdfError && (
                  <Typography color="error" style={{ marginTop: 8 }}>{pdfError}</Typography>
                )}
                {pdfResult && pdfResult.quiz && Array.isArray(pdfResult.quiz) ? (
                  <Box mt={2} width="100%">
                    <Typography variant="subtitle1">Quiz Extracted from PDF:</Typography>
                    {pdfResult.quiz.map((q: any, idx: number) => (
                      <Paper key={idx} style={{ margin: '12px 0', padding: 12, background: '#f5f5f5' }}>
                        <Typography variant="body1"><b>Q{idx + 1}:</b> {q.question}</Typography>
                        {q.choices && Array.isArray(q.choices) && (
                          <ul style={{ textAlign: 'left' }}>
                            {q.choices.map((choice: string, cidx: number) => (
                              <li key={cidx}>{choice}</li>
                            ))}
                          </ul>
                        )}
                        {q.answer && (
                          <Typography variant="body2" color="primary"><b>Answer:</b> {q.answer}</Typography>
                        )}
                      </Paper>
                    ))}
                  </Box>
                ) : pdfResult ? (
                  <Box mt={2} width="100%">
                    <Typography variant="subtitle1">Parsed PDF Result:</Typography>
                    <Paper style={{ maxHeight: 200, overflow: 'auto', padding: 8, background: '#f5f5f5' }}>
                      <pre style={{ textAlign: 'left', margin: 0 }}>{JSON.stringify(pdfResult, null, 2)}</pre>
                    </Paper>
                  </Box>
                ) : null}
              </Box>
            </Paper>
          </AccordionDetails>
        </Accordion>
        {/* Section 2: Ask Bedrock */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Ask Bedrock (AI Q&A)</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box display="flex" flexDirection="column" alignItems="center" width="100%">
              <Input
                placeholder="Type your question..."
                value={question}
                onChange={e => setQuestion(e.target.value)}
                style={{ width: '100%', marginBottom: 12 }}
                disabled={bedrockLoading}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleAskBedrock}
                disabled={!question.trim() || bedrockLoading}
              >
                {bedrockLoading ? 'Asking...' : 'Ask'}
              </Button>
              {bedrockError && (
                <Typography color="error" style={{ marginTop: 8 }}>{bedrockError}</Typography>
              )}
              {bedrockAnswer && (
                <Box mt={2} width="100%">
                  <Typography variant="subtitle1">Bedrock Answer:</Typography>
                  <Paper style={{ maxHeight: 200, overflow: 'auto', padding: 8, background: '#f5f5f5' }}>
                    <pre style={{ textAlign: 'left', margin: 0 }}>{bedrockAnswer}</pre>
                  </Paper>
                </Box>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
        {/* Section 3: Burnout Prevention */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Burnout Prevention</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2">(Functionality for burnout prevention goes here.)</Typography>
          </AccordionDetails>
        </Accordion>
      </Container>
    </div>
  );
}

export default App;
