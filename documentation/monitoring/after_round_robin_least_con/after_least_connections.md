➜  ProjetSession_LOG430 git:(main) ✗ ./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con"             
[2025-06-24 15:14:07] 🚀 Début des tests de charge automatisés
[2025-06-24 15:14:07] 📊 Configuration: 10 utilisateurs virtuels
[2025-06-24 15:14:07] ⏰ Heure de début: 2025-06-24T19:14:07
[2025-06-24 15:14:07] 📁 Rapport: after_round_robin_least_con/round_robin_least_con

[2025-06-24 15:14:07] 🔥 Lancement du test 1/3 (5 minutes)

         /\      Grafana   /‾‾/  
    /\  /  \     |\  __   /  /   
   /  \/    \    | |/ /  /   ‾‾\ 
  /          \   |   (  |  (‾)  |
 / __________ \  |_|\_\  \_____/ 

     execution: local
        script: monitoring/load_test.js
        output: -

     scenarios: (100.00%) 1 scenario, 10 max VUs, 5m30s max duration (incl. graceful stop):
              * default: 10 looping VUs for 5m0s (gracefulStop: 30s)

INFO[0000] Starting load test setup...                   source=console
INFO[0000] Testing authentication for all users...       source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ User manager authenticated successfully     source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ User employee authenticated successfully    source=console
INFO[0000] API is accessible and authentication is working, starting load test...  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0007] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0301] Load test completed                           source=console
INFO[0301] Total API calls made: undefined               source=console
INFO[0301] Authentication failures: undefined            source=console
INFO[0301] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.00%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=21.32ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 17938   59.527266/s
    checks_succeeded...................: 100.00% 17938 out of 17938
    checks_failed......................: 0.00%   0 out of 17938

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✓ get products status 200
    ✓ products has data
    ✓ products has pagination
    ✓ store products status valid
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format
    ✓ report valid response

    CUSTOM
    api_calls_total.........................................................: 11931  39.593032/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 11931
    login_duration..........................................................: avg=10.517091 min=1.958    med=11.265 max=19.824   p(90)=19.469  p(95)=19.5014

    HTTP
    http_req_duration.......................................................: avg=8.97ms    min=1.25ms   med=7.37ms max=165.96ms p(90)=16.08ms p(95)=21.32ms
      { expected_response:true }............................................: avg=8.97ms    min=1.25ms   med=7.37ms max=165.96ms p(90)=16.08ms p(95)=21.32ms
    http_req_failed.........................................................: 0.00%  0 out of 11954
    http_reqs...............................................................: 11954  39.669358/s

    EXECUTION
    iteration_duration......................................................: avg=1.54s     min=530.08ms med=1.53s  max=2.61s    p(90)=2.33s   p(95)=2.45s  
    iterations..............................................................: 1950   6.471076/s
    vus.....................................................................: 5      min=5          max=10
    vus_max.................................................................: 10     min=10         max=10

    NETWORK
    data_received...........................................................: 13 MB  44 kB/s
    data_sent...............................................................: 4.3 MB 14 kB/s




running (5m01.3s), 00/10 VUs, 1950 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  5m0s
[2025-06-24 15:19:08] ✅ Test 1/3 terminé

[2025-06-24 15:19:09] ⏸️  Pause de 1 minute avant le test 2/3
✅ Pause terminée!                              

[2025-06-24 15:20:09] 🔥 Lancement du test 2/3 (3 minutes)

         /\      Grafana   /‾‾/  
    /\  /  \     |\  __   /  /   
   /  \/    \    | |/ /  /   ‾‾\ 
  /          \   |   (  |  (‾)  |
 / __________ \  |_|\_\  \_____/ 

     execution: local
        script: monitoring/load_test.js
        output: -

     scenarios: (100.00%) 1 scenario, 10 max VUs, 3m30s max duration (incl. graceful stop):
              * default: 10 looping VUs for 3m0s (gracefulStop: 30s)

INFO[0000] Starting load test setup...                   source=console
INFO[0000] Testing authentication for all users...       source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ User manager authenticated successfully     source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ User employee authenticated successfully    source=console
INFO[0000] API is accessible and authentication is working, starting load test...  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0006] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0182] Load test completed                           source=console
INFO[0182] Total API calls made: undefined               source=console
INFO[0182] Authentication failures: undefined            source=console
INFO[0182] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.00%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=20.36ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 10642   58.387451/s
    checks_succeeded...................: 100.00% 10642 out of 10642
    checks_failed......................: 0.00%   0 out of 10642

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✓ get products status 200
    ✓ products has data
    ✓ products has pagination
    ✓ store products status valid
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format
    ✓ report valid response

    CUSTOM
    api_calls_total.........................................................: 7061   38.740255/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 7061
    login_duration..........................................................: avg=13.707364 min=2.416    med=13.8965 max=31.249  p(90)=20.8042 p(95)=28.40445

    HTTP
    http_req_duration.......................................................: avg=9.03ms    min=1.4ms    med=7.75ms  max=67.48ms p(90)=15.74ms p(95)=20.36ms 
      { expected_response:true }............................................: avg=9.03ms    min=1.4ms    med=7.75ms  max=67.48ms p(90)=15.74ms p(95)=20.36ms 
    http_req_failed.........................................................: 0.00%  0 out of 7084
    http_reqs...............................................................: 7084   38.866444/s

    EXECUTION
    iteration_duration......................................................: avg=1.56s     min=533.86ms med=1.55s   max=2.57s   p(90)=2.36s   p(95)=2.45s   
    iterations..............................................................: 1154   6.331434/s
    vus.....................................................................: 1      min=1         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 7.9 MB 43 kB/s
    data_sent...............................................................: 2.6 MB 14 kB/s




running (3m02.3s), 00/10 VUs, 1154 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  3m0s
[2025-06-24 15:23:12] ✅ Test 2/3 terminé

[2025-06-24 15:23:12] ⏸️  Pause de 1 minute avant le test 3/3
✅ Pause terminée!                              

[2025-06-24 15:24:12] 🔥 Lancement du test 3/3 (1 minute)

         /\      Grafana   /‾‾/  
    /\  /  \     |\  __   /  /   
   /  \/    \    | |/ /  /   ‾‾\ 
  /          \   |   (  |  (‾)  |
 / __________ \  |_|\_\  \_____/ 

     execution: local
        script: monitoring/load_test.js
        output: -

     scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration (incl. graceful stop):
              * default: 10 looping VUs for 1m0s (gracefulStop: 30s)

INFO[0000] Starting load test setup...                   source=console
INFO[0000] Testing authentication for all users...       source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ User manager authenticated successfully     source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ User employee authenticated successfully    source=console
INFO[0000] API is accessible and authentication is working, starting load test...  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0005] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0005] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0010] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0061] Load test completed                           source=console
INFO[0061] Total API calls made: undefined               source=console
INFO[0061] Authentication failures: undefined            source=console
INFO[0061] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.00%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=20.78ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 3612    58.483797/s
    checks_succeeded...................: 100.00% 3612 out of 3612
    checks_failed......................: 0.00%   0 out of 3612

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✓ get products status 200
    ✓ products has data
    ✓ products has pagination
    ✓ store products status valid
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ metrics accessible
    ✓ metrics format
    ✓ restock valid response
    ✓ report valid response

    CUSTOM
    api_calls_total.........................................................: 2366   38.309154/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 2366
    login_duration..........................................................: avg=15.505955 min=3.336    med=16.6935 max=25.6    p(90)=23.5374 p(95)=25.17425

    HTTP
    http_req_duration.......................................................: avg=9.19ms    min=1.38ms   med=7.87ms  max=61.93ms p(90)=16.16ms p(95)=20.78ms 
      { expected_response:true }............................................: avg=9.19ms    min=1.38ms   med=7.87ms  max=61.93ms p(90)=16.16ms p(95)=20.78ms 
    http_req_failed.........................................................: 0.00%  0 out of 2389
    http_reqs...............................................................: 2389   38.681559/s

    EXECUTION
    iteration_duration......................................................: avg=1.56s     min=548.93ms med=1.58s   max=2.59s   p(90)=2.34s   p(95)=2.45s   
    iterations..............................................................: 387    6.266121/s
    vus.....................................................................: 4      min=4         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 2.7 MB 44 kB/s
    data_sent...............................................................: 865 kB 14 kB/s




running (1m01.8s), 00/10 VUs, 387 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  1m0s
[2025-06-24 15:25:14] ✅ Test 3/3 terminé

[2025-06-24 15:25:14] 📈 Génération du rapport Prometheus...
[2025-06-24 15:25:14] ⏰ Période analysée: 2025-06-24T19:14:07 à 2025-06-24T19:25:14
[2025-06-24 15:25:14] 🐍 Création de l'environnement Python temporaire...
[2025-06-24 15:25:16] 📦 Installation des dépendances Python...
[2025-06-24 15:25:22] 📊 Exécution du script de génération de rapport...
/Users/erwanderrien/Desktop/LOG430/ProjetSession_LOG430/./monitoring/generate_prometheus_graphs.py:61: UserWarning: No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
  plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
PDF généré : documentation/monitoring/after_round_robin_least_con/round_robin_least_con.pdf
[2025-06-24 15:25:32] 🗑️  Suppression de l'environnement temporaire...
[2025-06-24 15:25:32] ✅ PDF généré avec succès: documentation/monitoring/after_round_robin_least_con/round_robin_least_con.pdf
[2025-06-24 15:25:32] 🎉 Automatisation terminée avec succès!

📋 Résumé:
   • Tests effectués: 3 (5min + 3min + 1min)
   • Utilisateurs virtuels: 10
   • Durée totale: ~11 minutes (tests + pauses)
   • Rapport: documentation/monitoring/after_round_robin_least_con/round_robin_least_con.pdf
   • Période: 2025-06-24T19:14:07 → 2025-06-24T19:25:14