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
      setFeedback({ message: 'Sincronização iniciada com sucesso!', type: 'success' });
      setUser('');
      setPassword('');
    } catch (err) {
      setFeedback({ message: 'Erro ao iniciar sincronização. Verifique as credenciais.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        Importação Manual de Aeroportos
      </Typography>
      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            label="Usuário"
            variant="outlined"
            fullWidth
            required
            margin="normal"
            value={user}
            onChange={(e) => setUser(e.target.value)}
          />
          <TextField
            label="Senha"
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
              Iniciar Sincronização
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