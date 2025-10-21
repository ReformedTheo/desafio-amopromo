

import React, { useState, useEffect, useMemo } from 'react';
import { getAirports } from '../services/api';
import { useNavigate } from 'react-router-dom'; 
import {
  Container, Typography, Box, TextField, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, CircularProgress
} from '@mui/material';

const Dashboard = () => {
  const [airports, setAirports] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate(); 


  useEffect(() => {
    const fetchAirports = async () => {
      try {
        const response = await getAirports();
        setAirports(response.data);
      } catch (err) {
        setError('Failed to fetch airports.');
      } finally {
        setLoading(false);
      }
    };
    fetchAirports();
  }, []);

  const filteredAirports = useMemo(() => {
    if (!searchTerm) return airports;
    return airports.filter(
      (airport) =>
        airport.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        airport.iata.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, airports]);


  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Airports Dashboard
      </Typography>
      <Box sx={{ mb: 3 }}>
        <TextField
          label="Filter by city or IATA"
          variant="outlined"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Box>
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
                <TableCell>IATA</TableCell>
                <TableCell>City</TableCell>
                <TableCell>State</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
             
              {filteredAirports.map((airport) => (
                <TableRow
                  key={airport.iata}
                  hover
                  onClick={() => navigate(`/airports/${airport.iata}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{airport.iata}</TableCell>
                  <TableCell>{airport.city}</TableCell>
                  <TableCell>{airport.state}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default Dashboard;