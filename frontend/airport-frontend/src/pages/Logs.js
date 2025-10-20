import React, { useState, useEffect } from 'react';
import { getImportLogs } from '../services/api';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Box, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, CircularProgress, Chip
} from '@mui/material';

const getStatusChip = (status) => {
  const statusMap = {
    SUCCESS: { label: 'Sucesso', color: 'success' },
    FAILURE: { label: 'Falha', color: 'error' },
    RUNNING: { label: 'Em Execução', color: 'warning' },
  };
  const { label, color } = statusMap[status] || { label: status, color: 'default' };
  return <Chip label={label} color={color} />;
};

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await getImportLogs();
        setLogs(response.data);
      } catch (err) {
        setError('Falha ao buscar o histórico.');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Histórico de Sincronização
      </Typography>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Data de Início</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Criados</TableCell>
                <TableCell>Atualizados</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log) => (
                <TableRow
                  key={log.id}
                  hover
                  onClick={() => navigate(`/logs/${log.id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{new Date(log.start_time).toLocaleString()}</TableCell>
                  <TableCell>{getStatusChip(log.status)}</TableCell>
                  <TableCell>{log.airports_created}</TableCell>
                  <TableCell>{log.airports_updated}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default Logs;