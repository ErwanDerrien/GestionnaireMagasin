# ➜  ProjetSession_LOG430 git:(main) ✗ k6 run --vus 10 --duration 1m monitoring/load_test.js

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
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0007] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0008] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0062] Load test completed                           source=console
INFO[0062] Total API calls made: undefined               source=console
INFO[0062] Authentication failures: undefined            source=console
INFO[0062] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.00%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=21.22ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 3676    58.883761/s
    checks_succeeded...................: 100.00% 3676 out of 3676
    checks_failed......................: 0.00%   0 out of 3676

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
    ✓ report valid response
    ✓ metrics accessible
    ✓ metrics format

    CUSTOM
    api_calls_total.........................................................: 2410   38.604424/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 2410
    login_duration..........................................................: avg=9.950636 min=1.999    med=7.9455 max=36.351  p(90)=17.0552 p(95)=19.63015

    HTTP
    http_req_duration.......................................................: avg=8.25ms   min=1.26ms   med=6.68ms max=69.83ms p(90)=16.05ms p(95)=21.22ms 
      { expected_response:true }............................................: avg=8.25ms   min=1.26ms   med=6.68ms max=69.83ms p(90)=16.05ms p(95)=21.22ms 
    http_req_failed.........................................................: 0.00%  0 out of 2433
    http_reqs...............................................................: 2433   38.972848/s

    EXECUTION
    iteration_duration......................................................: avg=1.55s    min=546.26ms med=1.55s  max=2.61s   p(90)=2.34s   p(95)=2.44s   
    iterations..............................................................: 393    6.295244/s
    vus.....................................................................: 1      min=1         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 2.9 MB 47 kB/s
    data_sent...............................................................: 886 kB 14 kB/s




running (1m02.4s), 00/10 VUs, 393 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  1m0s


# ➜  ProjetSession_LOG430 git:(main) ✗ k6 run --vus 10 --duration 3m monitoring/load_test.js

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
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0007] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0181] Load test completed                           source=console
INFO[0181] Total API calls made: undefined               source=console
INFO[0181] Authentication failures: undefined            source=console
INFO[0181] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.07%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=19.25ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.07%


  █ TOTAL RESULTS 

    checks_total.......................: 10586  58.198821/s
    checks_succeeded...................: 99.85% 10571 out of 10586
    checks_failed......................: 0.14%  15 out of 10586

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✗ get products status 200
      ↳  99% — ✓ 1141 / ✗ 5
    ✗ products has data
      ↳  99% — ✓ 1141 / ✗ 5
    ✗ products has pagination
      ↳  99% — ✓ 1141 / ✗ 5
    ✓ store products status valid
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ report valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format

    CUSTOM
    api_calls_total.........................................................: 7030   38.648943/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.07%  5 out of 7030
    login_duration..........................................................: avg=6.238955 min=1.689    med=5.765  max=13.158  p(90)=10.363  p(95)=11.6939

    HTTP
    http_req_duration.......................................................: avg=7.68ms   min=928µs    med=6.18ms max=56.74ms p(90)=14.54ms p(95)=19.25ms
      { expected_response:true }............................................: avg=7.67ms   min=928µs    med=6.18ms max=56.74ms p(90)=14.52ms p(95)=19.25ms
    http_req_failed.........................................................: 0.07%  5 out of 7053
    http_reqs...............................................................: 7053   38.775391/s

    EXECUTION
    iteration_duration......................................................: avg=1.57s    min=536.12ms med=1.59s  max=2.57s   p(90)=2.35s   p(95)=2.44s  
    iterations..............................................................: 1146   6.300382/s
    vus.....................................................................: 5      min=5         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 8.1 MB 45 kB/s
    data_sent...............................................................: 2.6 MB 14 kB/s




running (3m01.9s), 00/10 VUs, 1146 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  3m0s
➜  ProjetSession_LOG430 git:(main) ✗ 

# ➜  ProjetSession_LOG430 git:(main) ✗ k6 run --vus 10 --duration 5m monitoring/load_test.js

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
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0006] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0009] ✓ Authentication successful for user manager (store: 0)  source=console
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
    ✓ 'p(95)<2000' p(95)=20.21ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 17864   59.185962/s
    checks_succeeded...................: 100.00% 17864 out of 17864
    checks_failed......................: 0.00%   0 out of 17864

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
    ✓ report valid response
    ✓ metrics accessible
    ✓ metrics format

    CUSTOM
    api_calls_total.........................................................: 11885  39.376688/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 11885
    login_duration..........................................................: avg=10.711727 min=1.759    med=10.924 max=26.048  p(90)=17.3952 p(95)=18.4562

    HTTP
    http_req_duration.......................................................: avg=8.07ms    min=976µs    med=6.46ms max=89.66ms p(90)=15.36ms p(95)=20.21ms
      { expected_response:true }............................................: avg=8.07ms    min=976µs    med=6.46ms max=89.66ms p(90)=15.36ms p(95)=20.21ms
    http_req_failed.........................................................: 0.00%  0 out of 11908
    http_reqs...............................................................: 11908  39.45289/s

    EXECUTION
    iteration_duration......................................................: avg=1.54s     min=530.66ms med=1.56s  max=2.61s   p(90)=2.33s   p(95)=2.45s  
    iterations..............................................................: 1943   6.437434/s
    vus.....................................................................: 3      min=3          max=10
    vus_max.................................................................: 10     min=10         max=10

    NETWORK
    data_received...........................................................: 14 MB  45 kB/s
    data_sent...............................................................: 4.4 MB 14 kB/s




running (5m01.8s), 00/10 VUs, 1943 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  5m0s
➜  ProjetSession_LOG430 git:(main) ✗ 