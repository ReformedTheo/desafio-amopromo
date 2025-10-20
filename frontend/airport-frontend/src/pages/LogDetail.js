import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getImportLogById } from '../services/api';
import { Container, Typography, Box, Paper, CircularProgress, Button, Grid } from '@mui/material';

const DetailItem = ({ title, content }) => (
  <Grid item xs={12} sm={6}>
    <Typography variant="subtitle1" color="text.secondary">{title}</Typography>
    <Typography variant="body1">{content}</Typography>
  </Grid>
);

const LogDetail = () => {
  const { id } = useParams();
  const [log, setLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLog = async () => {
      try {
        const response = await getImportLogById(id);
        setLog(response.data);
      } catch (err) {
        setError('Falha ao buscar detalhes do log.');
      } finally {
        setLoading(false);
      }
    };
    fetchLog();
  }, [id]);

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!log) return <Typography>Log não encontrado.</Typography>;

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          Detalhes da Sincronização #{log.id}
        </Typography>
        <Button variant="outlined" onClick={() => navigate('/logs')}>Voltar</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Grid container spacing={2}>
          <DetailItem title="Status" content={log.status} />
          <DetailItem title="Início" content={new Date(log.start_time).toLocaleString()} />
          <DetailItem title="Fim" content={log.end_time ? new Date(log.end_time).toLocaleString() : 'N/A'} />
          <DetailItem title="Criados" content={log.airports_created} />
          <DetailItem title="Atualizados" content={log.airports_updated} />
        </Grid>
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6">IATA Codes Criados</Typography>
          <Paper variant="outlined" sx={{ p: 2, maxHeight: 150, overflow: 'auto', mt: 1, bgcolor: '#f5f5f5' }}>
            {log.created_iatas.length > 0 ? log.created_iatas.join(', ') : 'Nenhum'}
          </Paper>
        </Box>
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">IATA Codes Atualizados</Typography>
          <Paper variant="outlined" sx={{ p: 2, maxHeight: 150, overflow: 'auto', mt: 1, bgcolor: '#f5f5f5' }}>
            {log.updated_iatas.length > 0 ? log.updated_iatas.join(', ') : 'Nenhum'}
          </Paper>
        </Box>
        {log.error_message && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" color="error">Mensagem de Erro</Typography>
            <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#fff0f0' }}>
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{log.error_message}</pre>
            </Paper>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default LogDetail;