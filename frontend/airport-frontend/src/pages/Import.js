import React, { useState } from 'react';
import { triggerImport } from '../services/api';
import { Container, Typography, Box, TextField, Button, Paper, Alert, CircularProgress } from '@mui/material';

const Import = () => {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [feedback, setFeedback] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFeedback({ message: '', type: '' });
    try {
      await triggerImport(user, password);
      setFeedback({ message: 'Synchronization started successfully!', type: 'success' });
      setUser('');
      setPassword('');
    } catch (err) {
      setFeedback({ message: 'Failed to start synchronization. Check credentials and try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        Manual Airport Import
      </Typography>
      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
      <TextField
        label="User"
            variant="outlined"
            fullWidth
            required
            margin="normal"
            value={user}
            onChange={(e) => setUser(e.target.value)}
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            fullWidth
            required
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Box sx={{ mt: 2, position: 'relative' }}>
            <Button type="submit" variant="contained" fullWidth disabled={loading}>
              Start Synchronization
            </Button>
            {loading && (
              <CircularProgress
                size={24}
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginTop: '-12px',
                  marginLeft: '-12px',
                }}
              />
            )}
          </Box>
        </Box>
          {feedback.message && (
            <Alert severity={feedback.type} sx={{ mt: 3 }}>
              {feedback.message}
            </Alert>
          )}
      </Paper>
    </Container>
  );
};

export default Import;