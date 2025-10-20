import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
});

// --- Funções da API de Aeroportos ---

/**
 * Busca a lista de todos os aeroportos.
 * @returns {Promise<Array<object>>}
 */
export const getAirports = () => {
  return api.get('/airports/');
};

/**
 * Dispara a sincronização de aeroportos.
 * @param {string} user - O nome do usuário.
 * @param {string} password - A senha.
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

// --- Funções da API de Logs ---

/**
 * Busca o histórico de sincronizações.
 * @returns {Promise<Array<object>>}
 */
export const getImportLogs = () => {
  return api.get('/import-logs/');
};

/**
 * Busca os detalhes de um log específico.
 * @param {number} id - O ID do log.
 * @returns {Promise<object>}
 */
export const getImportLogById = (id) => {
  return api.get(`/import-logs/${id}/`);
};

/**
 * Busca os detalhes de um aeroporto específico pelo ID.
 * @param {string} iata - O código IATA do aeroporto.
 * @returns {Promise<object>}
 */
export const getAirportByIataCode = (iata) => {
  return api.get(`/airports/${iata}/`);
};


// --- Funções da API de Voos ---


/**
 * Busca combinações de voos com base nos critérios de pesquisa.
 * @param {object} params - Os parâmetros de busca.
 * @param {string} params.from - IATA do aeroporto de origem.
 * @param {string} params.to - IATA do aeroporto de destino.
 * @param {string} params.departureDate - Data de partida (YYYY-MM-DD).
 * @param {string} [params.returnDate] - Data do retorno opcional
 * @param {string} params.apiAuthToken - Auth Token.
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