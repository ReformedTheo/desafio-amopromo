import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
});

// --- Airport API functions ---

/**
 * Fetch the list of all airports.
 * @returns {Promise<Array<object>>}
 */
export const getAirports = () => {
  return api.get('/airports/');
};

/**
 * Trigger the airports synchronization process.
 * @param {string} user - Username for external API (if required).
 * @param {string} password - Password for external API (if required).
 * @returns {Promise<object>}
 */
export const triggerImport = (user, password) => {
  const formData = new FormData();
  formData.append('user', user);
  formData.append('password', password);

  return api.post('/airports/import/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// --- Import Logs API functions ---

/**
 * Fetch synchronization history logs.
 * @returns {Promise<Array<object>>}
 */
export const getImportLogs = () => {
  return api.get('/import-logs/');
};

/**
 * Fetch details for a specific import log.
 * @param {number} id - Log ID.
 * @returns {Promise<object>}
 */
export const getImportLogById = (id) => {
  return api.get(`/import-logs/${id}/`);
};

/**
 * Fetch details for a specific airport by IATA code.
 * @param {string} iata - Airport IATA code.
 * @returns {Promise<object>}
 */
export const getAirportByIataCode = (iata) => {
  return api.get(`/airports/${iata}/`);
};


// --- Flights API functions ---

/**
 * Search for flight combinations based on search criteria.
 * @param {object} params - Search parameters.
 * @param {string} params.from - Origin IATA.
 * @param {string} params.to - Destination IATA.
 * @param {string} params.departureDate - Departure date (YYYY-MM-DD).
 * @param {string} [params.returnDate] - Optional return date.
 * @param {string} params.apiAuthToken - API auth token.
 * @returns {Promise<object>}
 */
export const searchFlights = ({ from, to, departureDate, returnDate, apiAuthToken }) => {
  const queryParams = new URLSearchParams({
    from,
    to,
    departureDate,
  });

  if (returnDate) {
    queryParams.append('returnDate', returnDate);
  }

  return api.get(`/flights_integration/search/?${queryParams.toString()}`, {
    headers: {
      'Authorization': `Token ${apiAuthToken}`,
    },
  });
};


export default api;