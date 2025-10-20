import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAirportByIataCode } from '../services/api';
import { Container, Typography, Box, Paper, CircularProgress, Button, Grid } from '@mui/material';

const DetailItem = ({ title, content }) => (
  <Grid item xs={12} sm={6}>
    <Typography variant="subtitle1" color="text.secondary" gutterBottom>
      {title}
    </Typography>
    <Typography variant="h6">{content}</Typography>
  </Grid>
);

const AirportDetail = () => {
  const { iata } = useParams();
  const [airport, setAirport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAirport = async () => {
      if (!iata) return;
      setLoading(true);
      try {
        const response = await getAirportByIataCode(iata);
        setAirport(response.data);
      } catch (err) {
        setError('Falha ao buscar detalhes do aeroporto.');
      } finally {
        setLoading(false);
      }
    };
    fetchAirport();
  }, [iata]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Typography color="error" align="center">{error}</Typography>;
  }

  if (!airport) {
    return <Typography align="center">Aeroporto não encontrado.</Typography>;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Detalhes do Aeroporto
        </Typography>
        <Button variant="outlined" onClick={() => navigate('/')}>
          Voltar para a Lista
        </Button>
      </Box>
      <Paper sx={{ p: 4 }}>
        <Grid container spacing={3}>
          <DetailItem title="Código IATA" content={airport.iata} />
          <DetailItem title="Cidade" content={airport.city} />
          <DetailItem title="Estado" content={airport.state} />
          <DetailItem title="Latitude" content={airport.lat || 'N/A'} />
          <DetailItem title="Longitude" content={airport.lon || 'N/A'} />
        </Grid>
      </Paper>
    </Container>
  );
};

export default AirportDetail;