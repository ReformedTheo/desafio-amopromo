import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Import from './pages/Import';
import Logs from './pages/Logs';
import LogDetail from './pages/LogDetail';
import AirportDetail from './pages/AirportDetail';
import FlightSearch from './pages/FlightSearch'; 

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/airports/:iata" element={<AirportDetail />} />
        <Route path="/import" element={<Import />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/logs/:id" element={<LogDetail />} />
        <Route path="/flights_integration" element={<FlightSearch />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;