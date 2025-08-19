import React, { useState } from 'react';
import '../App.css';
import { Container, Typography, Box, Button, Input, Paper, Accordion, AccordionSummary, AccordionDetails, AppBar, Toolbar, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import axios from 'axios'; // Folosim axios pentru a gestiona mai usor headerele
import { useAuth } from '../context/AuthContext';

export function DashboardPage() {
  const { logout, token } = useAuth(); // Preluam functia de logout si token-ul din context

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

  const createApiHeaders = () => {
    return {
      'Authorization': `Bearer ${token}`
    };
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setPdfLoading(true);
    setPdfError(null);
    setPdfResult(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Am schimbat fetch cu axios pentru a trimite header-ul
      const response = await axios.post('/knowledge-graph/', formData, {
        headers: createApiHeaders()
      });

      setPdfResult(response.data);
    } catch (err: any) {
      setPdfError(err.response?.data?.detail || 'Failed to parse PDF');
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
      const response = await axios.post('/invoke-bedrock/', { question }, {
        headers: createApiHeaders()
      });

      setBedrockAnswer(response.data.result || JSON.stringify(response.data));
    } catch (err: any) {
      setBedrockError(err.response?.data?.detail || 'Failed to get answer');
    } finally {
      setBedrockLoading(false);
    }
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MindBoost Dashboard
          </Typography>
          <IconButton color="inherit" onClick={logout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
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
          {/* Section 1: Upload Materials & Knowledge Graph */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Upload to Generate Knowledge Graph</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Paper elevation={3} className="upload-section" style={{ width: '100%', padding: '16px' }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <label htmlFor="file-upload">
                    <Input id="file-upload" type="file" onChange={handleFileChange} style={{ display: 'none' }} />
                    <Button variant="contained" color="primary" component="span">
                      Choose File
                    </Button>
                  </label>
                  {fileName && <Typography variant="body2" style={{ marginTop: 12 }}>Selected: {fileName}</Typography>}
                  <Button variant="contained" color="secondary" style={{ marginTop: 16 }} onClick={handleUpload} disabled={!selectedFile || pdfLoading}>
                    {pdfLoading ? 'Generating...' : 'Generate Graph'}
                  </Button>
                  {pdfError && <Typography color="error" style={{ marginTop: 8 }}>{pdfError}</Typography>}
                  {pdfResult && (
                    <Box mt={2} width="100%">
                      <Typography variant="subtitle1">Graph Data:</Typography>
                      <Paper style={{ maxHeight: 200, overflow: 'auto', padding: 8, background: '#f5f5f5' }}>
                        <pre style={{ textAlign: 'left', margin: 0 }}>{JSON.stringify(pdfResult, null, 2)}</pre>
                      </Paper>
                    </Box>
                  )}
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
                <Input placeholder="Type your question..." value={question} onChange={e => setQuestion(e.target.value)} style={{ width: '100%', marginBottom: 12 }} disabled={bedrockLoading} />
                <Button variant="contained" color="primary" onClick={handleAskBedrock} disabled={!question.trim() || bedrockLoading}>
                  {bedrockLoading ? 'Asking...' : 'Ask'}
                </Button>
                {bedrockError && <Typography color="error" style={{ marginTop: 8 }}>{bedrockError}</Typography>}
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
        </Container>
      </div>
    </>
  );
}