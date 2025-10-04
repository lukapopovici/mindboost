import React, { useState } from 'react';
import '../App.css';
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  Input, 
  Paper, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails, 
  AppBar, 
  Toolbar, 
  IconButton,
  Chip,
  LinearProgress,
  Alert,
  Snackbar
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import PsychologyIcon from '@mui/icons-material/Psychology';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import ScienceIcon from '@mui/icons-material/Science';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

export function DashboardPage() {
  const { logout, token } = useAuth();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [pdfResult, setPdfResult] = useState<any>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const [question, setQuestion] = useState('');
  const [bedrockAnswer, setBedrockAnswer] = useState<string | null>(null);
  const [bedrockLoading, setBedrockLoading] = useState(false);
  const [bedrockError, setBedrockError] = useState<string | null>(null);

  const [burnoutModalOpen, setBurnoutModalOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

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

  const handleBurnoutCheck = () => {
    setSnackbarMessage('🧠 Burnout assessment feature coming soon! We\'re developing an AI-powered tool to help you recognize early signs of academic burnout.');
    setSnackbarOpen(true);
  };

  return (
    <>
      {/* Beautiful Academic Header */}
      <AppBar position="static" className="custom-appbar" elevation={0}>
        <Toolbar sx={{ padding: '8px 24px' }}>
          <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
            <PsychologyIcon sx={{ marginRight: 2, fontSize: '2rem' }} />
            <Typography variant="h6" component="div" className="appbar-title">
              MindBoost Analytics
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={2}>
            <Chip 
              label="Academic Mode" 
              size="small" 
              sx={{ 
                background: 'rgba(255,255,255,0.2)', 
                color: 'white',
                fontWeight: 500
              }} 
            />
            <IconButton 
              color="inherit" 
              onClick={logout}
              sx={{ 
                background: 'rgba(255,255,255,0.1)',
                '&:hover': { background: 'rgba(255,255,255,0.2)' }
              }}
            >
              <LogoutIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <div className="App">
        {/* Stunning Hero Header */}
        <header className="App-header">
          <Typography variant="h1" component="h1" className="main-title">
            MindBoost AI
          </Typography>
          <Typography variant="h4" component="h2" className="subtitle">
            Your Intelligent Academic Companion for Personalized Learning & Well-being
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center', mt: 2 }}>
            <Chip 
              icon={<ScienceIcon />} 
              label="Knowledge Graphs" 
              sx={{ 
                background: 'rgba(255,255,255,0.15)', 
                color: 'white',
                backdropFilter: 'blur(10px)'
              }} 
            />
            <Chip 
              icon={<PsychologyIcon />} 
              label="AI-Powered" 
              sx={{ 
                background: 'rgba(255,255,255,0.15)', 
                color: 'white',
                backdropFilter: 'blur(10px)'
              }} 
            />
            <Chip 
              icon={<QuestionAnswerIcon />} 
              label="Smart Q&A" 
              sx={{ 
                background: 'rgba(255,255,255,0.15)', 
                color: 'white',
                backdropFilter: 'blur(10px)'
              }} 
            />
          </Box>
          <Button 
            variant="contained" 
            className="burnout-button"
            onClick={handleBurnoutCheck}
            startIcon={<PsychologyIcon />}
            size="large"
          >
            Am I burnt out?
          </Button>
        </header>

        <Container className="content-container">
          {/* Knowledge Graph Upload Section */}
          <Accordion className="feature-card" defaultExpanded>
            <AccordionSummary 
              expandIcon={<ExpandMoreIcon />}
              aria-controls="upload-content"
              id="upload-header"
            >
              <Box display="flex" alignItems="center" gap={2}>
                <CloudUploadIcon color="primary" />
                <Typography variant="h6" className="section-title">
                  Generate Knowledge Graph
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box className="upload-section">
                <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
                  <Typography variant="body1" color="textSecondary" textAlign="center">
                    Upload your study materials to generate an intelligent concept map
                  </Typography>
                  
                  <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                    <Input 
                      id="file-upload" 
                      type="file" 
                      onChange={handleFileChange} 
                      style={{ display: 'none' }} 
                      inputProps={{ accept: '.pdf,.doc,.docx,.txt' }}
                    />
                    <Button 
                      variant="contained" 
                      color="primary" 
                      component="span"
                      startIcon={<CloudUploadIcon />}
                      size="large"
                      sx={{ minWidth: 200 }}
                    >
                      Choose File
                    </Button>
                  </label>
                  
                  {fileName && (
                    <Chip 
                      label={`Selected: ${fileName}`} 
                      color="primary" 
                      variant="outlined"
                      sx={{ maxWidth: 300 }}
                    />
                  )}
                  
                  <Button 
                    variant="contained" 
                    color="secondary" 
                    onClick={handleUpload} 
                    disabled={!selectedFile || pdfLoading}
                    startIcon={<ScienceIcon />}
                    size="large"
                    sx={{ minWidth: 200 }}
                  >
                    {pdfLoading ? 'Generating Graph...' : 'Generate Knowledge Graph'}
                  </Button>
                  
                  {pdfLoading && (
                    <Box sx={{ width: '100%', maxWidth: 400 }}>
                      <LinearProgress />
                      <Typography variant="body2" textAlign="center" sx={{ mt: 1 }}>
                        Processing your document...
                      </Typography>
                    </Box>
                  )}
                  
                  {pdfError && (
                    <Alert severity="error" sx={{ width: '100%', maxWidth: 400 }}>
                      {pdfError}
                    </Alert>
                  )}
                  
                  {pdfResult && (
                    <Box sx={{ width: '100%' }}>
                      <Typography variant="h6" gutterBottom color="primary">
                        📊 Knowledge Graph Generated
                      </Typography>
                      <Paper className="result-container" elevation={0}>
                        <pre>{JSON.stringify(pdfResult, null, 2)}</pre>
                      </Paper>
                    </Box>
                  )}
                </Box>
              </Box>
            </AccordionDetails>
          </Accordion>
          
          {/* AI Q&A Section */}
          <Accordion className="feature-card">
            <AccordionSummary 
              expandIcon={<ExpandMoreIcon />}
              aria-controls="qa-content"
              id="qa-header"
            >
              <Box display="flex" alignItems="center" gap={2}>
                <QuestionAnswerIcon color="primary" />
                <Typography variant="h6" className="section-title">
                  AI Study Assistant
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box display="flex" flexDirection="column" gap={3}>
                <Typography variant="body1" color="textSecondary" textAlign="center">
                  Ask questions about your study materials and get intelligent answers
                </Typography>
                
                <Input 
                  placeholder="What would you like to know about your study materials?" 
                  value={question} 
                  onChange={e => setQuestion(e.target.value)}
                  disabled={bedrockLoading}
                  multiline
                  rows={3}
                  sx={{ 
                    width: '100%',
                    padding: 2,
                    border: '1px solid var(--silver-blue)',
                    borderRadius: '12px'
                  }}
                />
                
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={handleAskBedrock} 
                  disabled={!question.trim() || bedrockLoading}
                  startIcon={<QuestionAnswerIcon />}
                  size="large"
                  sx={{ alignSelf: 'center', minWidth: 200 }}
                >
                  {bedrockLoading ? 'Thinking...' : 'Ask AI Assistant'}
                </Button>
                
                {bedrockLoading && (
                  <Box sx={{ width: '100%' }}>
                    <LinearProgress />
                    <Typography variant="body2" textAlign="center" sx={{ mt: 1 }}>
                      AI is processing your question...
                    </Typography>
                  </Box>
                )}
                
                {bedrockError && (
                  <Alert severity="error" sx={{ width: '100%' }}>
                    {bedrockError}
                  </Alert>
                )}
                
                {bedrockAnswer && (
                  <Box sx={{ width: '100%' }}>
                    <Typography variant="h6" gutterBottom color="primary">
                      🤖 AI Response
                    </Typography>
                    <Paper className="result-container" elevation={0}>
                      <pre>{bedrockAnswer}</pre>
                    </Paper>
                  </Box>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        </Container>
      </div>

      {/* Notification Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity="info" 
          sx={{ width: '100%', maxWidth: 500 }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
}