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
    apiAuthToken: '', 
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
      const response = await searchFlights(params);
      setResults(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to search flights. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderFlightDetails = (flights, title) => (
    <Box mt={2}>
      <Typography variant="h6">{title}</Typography>
      <List dense>
        {flights.map((flight, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={`Aircraft: ${flight.aircraft.manufacturer} ${flight.aircraft.model}`}
              secondary={`Departure: ${new Date(flight.departure_time).toLocaleString()} - Arrival: ${new Date(flight.arrival_time).toLocaleString()}`}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Flight Search
      </Typography>
      <Paper sx={{ p: 4 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="from"
                label="Origin (IATA)"
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
                label="Destination (IATA)"
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
                label="Departure Date"
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
                label="Return Date"
                type="date"
                variant="outlined"
                fullWidth
                required
                value={params.returnDate}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
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
              Search
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
            Search Results
          </Typography>
          {results.combinations && results.combinations.length > 0 ? (
            results.combinations.map((combo, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" color="primary">
                  Option {index + 1} - Total Price: {combo.price.currency} {combo.price.total.toFixed(2)}
                </Typography>
                <Divider sx={{ my: 1 }} />
                {renderFlightDetails([combo.outbound_flight], 'Outbound Flight')}
                {combo.inbound_flight && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    {renderFlightDetails([combo.inbound_flight], 'Inbound Flight')}
                  </>
                )}
              </Paper>
            ))
          ) : (
            <Alert severity="info">No flight combinations found for the given criteria.</Alert>
          )}
        </Box>
      )}
    </Container>
  );
};

export default FlightSearch;