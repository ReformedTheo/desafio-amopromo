import React, { useState } from 'react';
import { searchFlights } from '../services/api';
import {
  Container, Typography, Box, Paper, TextField, Button, Grid,
  CircularProgress, Alert, List, ListItem, ListItemText, Divider
} from '@mui/material';

const FlightSearch = () => {
  const [params, setParams] = useState({
    from: '',
    to: '',
    departureDate: '',
    returnDate: '',
    apiAuthToken: '', // State to hold the API token
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setParams({ ...params, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Pass all params, including the token, to the service function
      const response = await searchFlights(params);
      setResults(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Erro ao buscar voos. Tente novamente.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderFlightDetails = (flights, title) => (
    <Box mt={2}>
      <Typography variant="h6">{title}</Typography>
      <List dense>
        {/* Note: The mock API response does not include flight_number, origin, or destination.
             This rendering part might need adjustment based on the actual API response structure.
             For now, using what's available in the provided data. */}
        {flights.map((flight, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={`Aeronave: ${flight.aircraft.manufacturer} ${flight.aircraft.model}`}
              secondary={`Partida: ${new Date(flight.departure_time).toLocaleString()} - Chegada: ${new Date(flight.arrival_time).toLocaleString()}`}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Buscar Voos
      </Typography>
      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="from"
                label="Origem (IATA)"
                variant="outlined"
                fullWidth
                required
                value={params.from}
                onChange={handleChange}
                inputProps={{ maxLength: 3, style: { textTransform: 'uppercase' } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="to"
                label="Destino (IATA)"
                variant="outlined"
                fullWidth
                required
                value={params.to}
                onChange={handleChange}
                inputProps={{ maxLength: 3, style: { textTransform: 'uppercase' } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="departureDate"
                label="Data de Partida"
                type="date"
                variant="outlined"
                fullWidth
                required
                value={params.departureDate}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="returnDate"
                label="Data de Retorno"
                type="date"
                variant="outlined"
                fullWidth
                required
                value={params.returnDate}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            {/* New API Token Field */}
            <Grid item xs={12}>
              <TextField
                name="apiAuthToken"
                label="API Token"
                type="password"
                variant="outlined"
                fullWidth
                required
                value={params.apiAuthToken}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 3, position: 'relative' }}>
            <Button type="submit" variant="contained" fullWidth disabled={loading}>
              Buscar
            </Button>
            {loading && (
              <CircularProgress
                size={24}
                sx={{ position: 'absolute', top: '50%', left: '50%', mt: '-12px', ml: '-12px' }}
              />
            )}
          </Box>
        </Box>
      </Paper>

      {error && <Alert severity="error" sx={{ mt: 3 }}>{error}</Alert>}

      {results && (
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            Resultados da Busca
          </Typography>
          {results.combinations && results.combinations.length > 0 ? (
            results.combinations.map((combo, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" color="primary">
                  Opção {index + 1} - Preço Total: {combo.price.currency} {combo.price.total.toFixed(2)}
                </Typography>
                <Divider sx={{ my: 1 }} />
                {renderFlightDetails([combo.outbound_flight], 'Voo de Ida')}
                {combo.inbound_flight && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    {renderFlightDetails([combo.inbound_flight], 'Voo de Volta')}
                  </>
                )}
              </Paper>
            ))
          ) : (
            <Alert severity="info">Nenhuma combinação de voos encontrada para os critérios informados.</Alert>
          )}
        </Box>
      )}
    </Container>
  );
};

export default FlightSearch;