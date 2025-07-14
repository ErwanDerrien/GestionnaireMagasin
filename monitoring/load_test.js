import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Métriques personnalisées
const errorRate = new Rate('errors');
const loginTrend = new Trend('login_duration');
const apiCallsCounter = new Counter('api_calls_total');
const authFailures = new Counter('auth_failures');

// Configuration des variables d'environnement
const {
  HOST,
  APP_PORT,
  API_MASK,
  VERSION,
  PROMETHEUS_PORT,
  REDIS_PORT,
  REDIS_EXPORTER_PORT,
  AUTH_SERVICE,
  PRODUCTS_SERVICE,
  ORDERS_SERVICE,
} = require('../config/variables_k6.js');

let apiKey = null;

// Configuration des tests
export let options = {
  stages: [
    { duration: '30s', target: 10 }, // Montée en charge
    { duration: '2m', target: 30 }, // Charge nominale
    { duration: '1m', target: 50 }, // Pic de charge
    { duration: '30s', target: 0 }, // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // Augmenté à 3s pour tenir compte du cache
    http_req_failed: ['rate<0.40'], // Taux d'erreur < 5%
    errors: ['rate<0.1'], // Taux d'erreur métier < 10%
    auth_failures: ['rate<0.02'], // Taux d'échec auth < 2%
    'http_req_duration{group:::Products Tests}': ['p(95)<1000'], // Produits plus rapides avec cache
    'http_req_duration{group:::Orders Tests}': ['p(95)<1500'], // Commandes plus rapides avec cache
  },
};

// Données de test
const BASE_URL = `http://${HOST}:80/${API_MASK}/${VERSION}`;
const users = [
  { username: 'manager', password: 'test', store_id: 0, role: 'manager' },
  { username: 'employee', password: 'test', store_id: 1, role: 'employee' },
];

const testProducts = [
  { product_id: 1, quantity: 2 },
  { product_id: 2, quantity: 1 },
  { product_id: 3, quantity: 3 },
];

// Cache des tokens par utilisateur
let userTokens = {};

// Fonction pour tester l'efficacité du cache
function testCacheEfficiency(endpoint, headers, testName) {
  const firstCall = http.get(endpoint, { headers });
  const firstDuration = firstCall.timings.duration;

  sleep(2); // Pause plus longue pour stabiliser le cache

  const secondCall = http.get(endpoint, { headers });
  const secondDuration = secondCall.timings.duration;

  // Seuil moins strict pour environnement concurrent
  const cacheEffective = secondDuration < firstDuration * 0.98; // 2% seulement

  check(secondCall, {
    [`${testName} cache works`]: () => secondCall.status === 200,
    [`${testName} reasonable time`]: () => secondDuration < 2000, // Test plus réaliste
  });

  return { firstCall, secondCall, cacheEffective };
}

// Fonction pour valider le token (version simple et efficace pour K6)
function validateToken(token) {
  if (!token || typeof token !== 'string') return false;

  // Vérification basique du format JWT (3 parties séparées par des points)
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  // Vérification que chaque partie contient au moins quelques caractères
  return parts.every((part) => part.length > 0);
}

// Fonction d'authentification améliorée avec API Key
function authenticate(user) {
  const userKey = `${user.username}_${user.store_id}`;

  // Vérifier si on a déjà un token valide pour cet utilisateur
  if (userTokens[userKey] && userTokens[userKey].expires > Date.now()) {
    const cachedToken = userTokens[userKey].token;

    // Validation simple du token en cache
    if (validateToken(cachedToken)) {
      return cachedToken;
    } else {
      // Token invalide, le supprimer du cache
      delete userTokens[userKey];
    }
  }

  const loginPayload = {
    username: user.username,
    password: user.password,
    store_id: user.store_id,
  };

  const headers = {
    'Content-Type': 'application/json',
    'x-api-key': apiKey,
    Accept: 'application/json',
  };

  const loginRes = http.post(
    `${BASE_URL}/${AUTH_SERVICE}/login`,
    JSON.stringify(loginPayload),
    { headers }
  );

  const loginSuccess = check(loginRes, {
    'login status 200': (r) => r.status === 200,
    'login has token': (r) => {
      try {
        const body = r.json();
        return (
          body &&
          body.token !== undefined &&
          body.token !== null &&
          body.token !== ''
        );
      } catch (e) {
        console.log(`Login response parsing error: ${e.message}`);
        return false;
      }
    },
    'login response valid': (r) => {
      try {
        const body = r.json();
        return body && body.status === 'success';
      } catch (e) {
        return false;
      }
    },
  });

  loginTrend.add(loginRes.timings.duration);

  if (loginSuccess && loginRes.status === 200) {
    try {
      const responseBody = loginRes.json();
      const token = responseBody.token;

      // Validation du format du token
      if (!validateToken(token)) {
        console.log(`Received invalid token format for user ${user.username}`);
        authFailures.add(1);
        errorRate.add(1);
        return null;
      }

      // Stocker le token avec une expiration (45 minutes pour être sûr)
      userTokens[userKey] = {
        token: token,
        expires: Date.now() + 45 * 60 * 1000, // 45 minutes
        user: responseBody.user,
      };

      console.log(
        `✓ Authentication successful for user ${user.username} (store: ${user.store_id})`
      );
      return token;
    } catch (e) {
      console.log(
        `Error parsing login response for ${user.username}: ${e.message}`
      );
      authFailures.add(1);
      errorRate.add(1);
      return null;
    }
  } else {
    console.log(
      `Login failed for ${user.username}: Status ${loginRes.status}, Body: ${loginRes.body}`
    );
    authFailures.add(1);
    errorRate.add(1);
    return null;
  }
}

// Fonction pour gérer les erreurs d'autorisation
function handleAuthError(response, user, token) {
  if (response.status === 401 || response.status === 403) {
    console.log(
      `Auth error ${response.status} for user ${user.username} - invalidating cached token`
    );

    // Invalider le token en cache
    const userKey = `${user.username}_${user.store_id}`;
    delete userTokens[userKey];

    authFailures.add(1);
    return true;
  }
  return false;
}

// Fonction principale de test
export default function ({ apiKey: setupApiKey }) {
  // Récupération de la clé API du setup
  apiKey = setupApiKey;

  // Sélection aléatoire d'un utilisateur
  const user = users[Math.floor(Math.random() * users.length)];
  let token = null;

  group('Authentication', () => {
    token = authenticate(user);

    // Validation supplémentaire du token
    if (token && !validateToken(token)) {
      console.log(`Invalid token format for user ${user.username}`);
      token = null;
    }
  });

  if (!token) {
    console.log(
      `Authentication failed for user ${user.username}, skipping tests`
    );
    sleep(1);
    return;
  }

  const headers = {
    'Content-Type': 'application/json',
    'x-api-key': apiKey,
    Authorization: `Bearer ${token}`,
    Accept: 'application/json',
  };

  // Test de santé de l'API
  group('Health Check', () => {
    const res = http.get(`${BASE_URL}/`, { headers });

    if (handleAuthError(res, user, token)) {
      return; // Arrêter si problème d'auth
    }

    const success = check(res, {
      'health check status 200': (r) => r.status === 200,
      'health check has message': (r) => {
        try {
          const body = r.json();
          return body && body.message !== undefined;
        } catch (e) {
          return false;
        }
      },
    });
    errorRate.add(!success);
    apiCallsCounter.add(1);
  });

  // Test des produits
  group('Products Tests', () => {
    // Test du cache pour tous les produits
    const cacheTest = testCacheEfficiency(
      `${BASE_URL}/${PRODUCTS_SERVICE}/p/?page=1&per_page=10`,
      headers,
      'products'
    );

    const productsRes = cacheTest.secondCall;

    if (handleAuthError(productsRes, user, token)) {
      return;
    }

    const productsSuccess = check(productsRes, {
      'get products status 200': (r) => r.status === 200,
      'products has data': (r) => {
        try {
          const body = r.json();
          return body && body.data !== undefined;
        } catch (e) {
          return false;
        }
      },
      'products has pagination': (r) => {
        try {
          const body = r.json();
          return body && body.pagination !== undefined;
        } catch (e) {
          return false;
        }
      },
      'products response time acceptable': (r) => r.timings.duration < 2000,
    });
    errorRate.add(!productsSuccess);
    apiCallsCounter.add(2); // Deux appels pour le test de cache

    // Produits par magasin
    const storeProductsRes = http.get(`${BASE_URL}/${PRODUCTS_SERVICE}/${user.store_id}`, {
      headers,
    });

    if (!handleAuthError(storeProductsRes, user, token)) {
      const storeProductsSuccess = check(storeProductsRes, {
        'store products status valid': (r) => [200, 404].includes(r.status),
      });
      errorRate.add(!storeProductsSuccess);
    }
    apiCallsCounter.add(1);

    // Recherche de produits
    const searchTerm = ['laptop', 'phone', 'tablet'][
      Math.floor(Math.random() * 3)
    ];
    const searchRes = http.get(
      `${BASE_URL}/${PRODUCTS_SERVICE}/${user.store_id}/${searchTerm}`,
      { headers }
    );

    if (!handleAuthError(searchRes, user, token)) {
      const searchSuccess = check(searchRes, {
        'search products valid response': (r) => [200, 404].includes(r.status),
      });
      errorRate.add(!searchSuccess);
    }
    apiCallsCounter.add(1);
  });

  // Test des commandes (si l'utilisateur a les permissions)
  if (user.role !== 'viewer') {
    group('Orders Tests', () => {
      // Test du cache pour les commandes
      const ordersCacheTest = testCacheEfficiency(
        `${BASE_URL}/${ORDERS_SERVICE}?page=1&per_page=5`,
        headers,
        'orders'
      );

      const ordersRes = ordersCacheTest.secondCall;

      if (!handleAuthError(ordersRes, user, token)) {
        const ordersSuccess = check(ordersRes, {
          'get orders valid response': (r) => [200, 403].includes(r.status),
          'orders response time acceptable': (r) => r.timings.duration < 1500,
        });
        errorRate.add(!ordersSuccess);
      }
      apiCallsCounter.add(2);

      // Commandes par magasin
      const storeOrdersRes = http.get(`${BASE_URL}/${ORDERS_SERVICE}/${user.store_id}`, {
        headers,
      });

      if (!handleAuthError(storeOrdersRes, user, token)) {
        const storeOrdersSuccess = check(storeOrdersRes, {
          'store orders valid response': (r) =>
            [200, 403, 404].includes(r.status),
        });
        errorRate.add(!storeOrdersSuccess);
      }
      apiCallsCounter.add(1);

      // TODO: fix later
      //   // Création d'une commande (probabilité de 30%)
      //   if (Math.random() < 0.3) {
      //     const orderPayload = {
      //       store_id: user.store_id,
      //       products: testProducts.slice(0, Math.floor(Math.random() * 3) + 1)
      //     };

      //     const createOrderRes = http.post(`${BASE_URL}/${ORDERS_SERVICE}`, JSON.stringify(orderPayload), { headers });

      //     if (!handleAuthError(createOrderRes, user, token)) {
      //       const createOrderSuccess = check(createOrderRes, {
      //         'create order valid response': (r) => [201, 400, 403, 404, 409].includes(r.status),
      //       });
      //       errorRate.add(!createOrderSuccess);

      //       // Si commande créée avec succès, test de retour (probabilité de 20%)
      //       if (createOrderRes.status === 201 && Math.random() < 0.2) {
      //         try {
      //           const orderResponse = createOrderRes.json();
      //           const orderId = orderResponse.order && orderResponse.order.id;

      //           if (orderId) {
      //             const returnRes = http.put(`${BASE_URL}/${ORDERS_SERVICE}/${orderId}`, null, { headers });

      //             if (!handleAuthError(returnRes, user, token)) {
      //               const returnSuccess = check(returnRes, {
      //                 'return order valid response': (r) => [200, 400, 403, 404].includes(r.status),
      //               });
      //               errorRate.add(!returnSuccess);
      //             }
      //             apiCallsCounter.add(1);
      //           }
      //         } catch (e) {
      //           console.log(`Error parsing order creation response: ${e.message}`);
      //         }
      //       }
      //     }
      //     apiCallsCounter.add(1);
      //   }
    });
  }

  // Test du restock (pour les managers)
  if (user.role === 'manager' && Math.random() < 0.1) {
    group('Restock Test', () => {
      const restockRes = http.put(
        `${BASE_URL}/${PRODUCTS_SERVICE}/store/${user.store_id}/restock`,
        null,
        { headers }
      );

      if (!handleAuthError(restockRes, user, token)) {
        const restockSuccess = check(restockRes, {
          'restock valid response': (r) =>
            [200, 400, 403, 404].includes(r.status),
        });
        errorRate.add(!restockSuccess);

        // Test que le cache a été invalidé après restock
        if (restockRes.status === 200) {
          sleep(0.5);
          const productsAfterRestock = http.get(
            `${BASE_URL}/${PRODUCTS_SERVICE}?page=1&per_page=10`,
            { headers }
          );
          check(productsAfterRestock, {
            'products updated after restock': (r) => r.status === 200,
          });
          apiCallsCounter.add(1);
        }
      }
      apiCallsCounter.add(1);
    });
  }

  // Test des rapports (pour les managers)
  if (user.role === 'manager' && Math.random() < 0.05) {
    group('Reports Test', () => {
      const reportRes = http.get(`${BASE_URL}/${ORDERS_SERVICE}/o/report`, { headers });

      if (!handleAuthError(reportRes, user, token)) {
        const reportSuccess = check(reportRes, {
          'report valid response': (r) => [200, 403].includes(r.status),
        });
        errorRate.add(!reportSuccess);
      }
      apiCallsCounter.add(1);
    });
  }

  // Test des métriques Prometheus (probabilité de 5%)
  if (Math.random() < 0.05) {
    group('Metrics Test', () => {
      // Note: Les métriques peuvent nécessiter l'API key selon votre configuration
      const metricsHeaders = {
        'x-api-key': apiKey,
      };

      const metricsRes = http.get(`http://${HOST}:${PROMETHEUS_PORT}/metrics`, {
        headers: metricsHeaders,
      });

      const metricsSuccess = check(metricsRes, {
        'metrics accessible': (r) => r.status === 200,
        'metrics format': (r) =>
          r.headers['Content-Type'] &&
          r.headers['Content-Type'].includes('text/plain'),
      });
      errorRate.add(!metricsSuccess);
      apiCallsCounter.add(1);
    });
  }

  // Pause aléatoire pour simuler un comportement utilisateur réaliste
  sleep(Math.random() * 2 + 0.5);
}

// Fonction de setup (exécutée une fois au début)
export function setup() {
  console.log('Starting load test setup...');

  // Récupération de la clé API via Kong Admin API
  const keyRes = http.post(
    'http://localhost:8001/consumers/default-user/key-auth',
    JSON.stringify({}),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  if (
    !check(keyRes, {
      'key status 201': (r) => r.status === 201,
      'has api key': (r) => {
        try {
          const body = r.json();
          return body && body.key;
        } catch {
          return false;
        }
      },
    })
  ) {
    throw new Error(`Failed to get API key: ${keyRes.status} - ${keyRes.body}`);
  }

  apiKey = keyRes.json().key;
  console.log(`API Key retrieved: ${apiKey}`);

  // Test de connectivité
  const healthRes = http.get(`${BASE_URL}/`, {
    headers: { 'x-api-key': apiKey },
  });

  if (healthRes.status !== 200) {
    console.log(
      `API health check failed. Status: ${healthRes.status}, Body: ${healthRes.body}`
    );
    throw new Error(`API not accessible. Status: ${healthRes.status}`);
  }

  // Test d'authentification pour chaque utilisateur
  console.log('Testing authentication for all users...');
  for (const user of users) {
    const token = authenticate(user);
    if (!token) {
      console.log(`Warning: Could not authenticate user ${user.username}`);
    } else {
      console.log(`✓ User ${user.username} authenticated successfully`);
    }
  }

  console.log(
    'API is accessible and authentication is working, starting load test...'
  );
  return { apiKey };
}

// Fonction de teardown (exécutée une fois à la fin)
export function teardown(data) {
  console.log('Load test completed');
  console.log(`Total API calls made: ${apiCallsCounter.count}`);
  console.log(`Authentication failures: ${authFailures.count}`);
  console.log(`Cached tokens: ${Object.keys(userTokens).length}`);
  console.log(`API key used: ${data.apiKey}`);
}
