
import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { Container, Typography, Box, Button, Input, Paper } from '@mui/material';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setFileName(event.target.files[0].name);
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
        <Paper elevation={3} className="upload-section">
          <Typography variant="h6" gutterBottom>
            Upload your study materials
          </Typography>
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
          </Box>
        </Paper>
      </Container>
    </div>
  );
}

export default App;
