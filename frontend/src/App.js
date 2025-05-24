import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, Box, AppBar, Toolbar, Typography } from '@mui/material';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Suporte N1 - Chatbot
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
          <Routes>
            <Route path="/" element={<ChatInterface />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;