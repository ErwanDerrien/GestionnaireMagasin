const fs = require('fs');
const path = require('path');

// Charger les variables depuis le fichier JSON
function loadVariables() {
  try {
    const filePath = path.join(__dirname, 'universal_variables.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Erreur lors du chargement des variables:', error);
    return {};
  }
}

// Exporter les variables
const vars = loadVariables();

module.exports = {
  HOST: vars.host,
  APP_PORT: vars.app_port,
  API_MASK: vars.api_mask,
  VERSION: vars.version,
  PROMETHEUS_PORT: vars.prometheus_port,
  REDIS_PORT: vars.redis_port,
  REDIS_EXPORTER_PORT: vars.redis_exporter_port,
  AUTH_SERVICE: vars.auth_service,
  PRODUCTS_SERVICE: vars.products_service,
  ORDERS_SERVICE: vars.orders_service
};

// Usage:
// const { HOST, APP_PORT, API_MASK, VERSION, PROMETHEUS_PORT, REDIS_PORT, REDIS_EXPORTER_PORT, AUTH_SERVICE, PRODUCTS_SERVICE, ORDERS_SERVICE } = require('./variables');
// console.log(HOST); // "localhost"
// console.log(APP_PORT); // "8080"
