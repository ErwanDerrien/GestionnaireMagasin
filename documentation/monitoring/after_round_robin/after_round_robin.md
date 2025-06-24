# ➜  ProjetSession_LOG430 git:(main) ✗ k6 run --vus 10 --duration **1m** monitoring/load_test.js

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
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0006] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0010] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0062] Load test completed                           source=console
INFO[0062] Total API calls made: undefined               source=console
INFO[0062] Authentication failures: undefined            source=console
INFO[0062] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.39%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=19.76ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.38%


  █ TOTAL RESULTS 

    checks_total.......................: 3489   55.7717/s
    checks_succeeded...................: 99.34% 3466 out of 3489
    checks_failed......................: 0.65%  23 out of 3489

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✗ get products status 200
      ↳  98% — ✓ 368 / ✗ 7
    ✗ products has data
      ↳  98% — ✓ 368 / ✗ 7
    ✗ products has pagination
      ↳  98% — ✓ 368 / ✗ 7
    ✗ store products status valid
      ↳  99% — ✓ 373 / ✗ 2
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format
    ✓ report valid response

    CUSTOM
    api_calls_total.........................................................: 2288   36.573703/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.39%  9 out of 2288
    login_duration..........................................................: avg=10.638182 min=2.627    med=10.462 max=17.656  p(90)=15.7987 p(95)=17.5333

    HTTP
    http_req_duration.......................................................: avg=8.84ms    min=1.22ms   med=7.46ms max=62.24ms p(90)=15.74ms p(95)=19.76ms
      { expected_response:true }............................................: avg=8.83ms    min=1.22ms   med=7.45ms max=62.24ms p(90)=15.68ms p(95)=19.77ms
    http_req_failed.........................................................: 0.38%  9 out of 2311
    http_reqs...............................................................: 2311   36.941358/s

    EXECUTION
    iteration_duration......................................................: avg=1.63s     min=550.62ms med=1.7s   max=2.58s   p(90)=2.39s   p(95)=2.47s  
    iterations..............................................................: 375    5.994379/s
    vus.....................................................................: 2      min=2         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 2.2 MB 36 kB/s
    data_sent...............................................................: 839 kB 13 kB/s




running (1m02.6s), 00/10 VUs, 375 complete and 0 interrupted iterations
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
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0005] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0007] ✓ Authentication successful for user employee (store: 1)  source=console
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
    ✓ 'p(95)<2000' p(95)=22.52ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 10717   58.801147/s
    checks_succeeded...................: 100.00% 10717 out of 10717
    checks_failed......................: 0.00%   0 out of 10717

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
    api_calls_total.........................................................: 7107   38.994099/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 7107
    login_duration..........................................................: avg=9.632091 min=2.29     med=7.413  max=32.032  p(90)=19.6657 p(95)=20.1998

    HTTP
    http_req_duration.......................................................: avg=9.05ms   min=1.46ms   med=7.09ms max=88.48ms p(90)=16.82ms p(95)=22.52ms
      { expected_response:true }............................................: avg=9.05ms   min=1.46ms   med=7.09ms max=88.48ms p(90)=16.82ms p(95)=22.52ms
    http_req_failed.........................................................: 0.00%  0 out of 7130
    http_reqs...............................................................: 7130   39.120293/s

    EXECUTION
    iteration_duration......................................................: avg=1.55s    min=529.09ms med=1.55s  max=2.58s   p(90)=2.36s   p(95)=2.44s  
    iterations..............................................................: 1164   6.386539/s
    vus.....................................................................: 1      min=1         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 7.9 MB 43 kB/s
    data_sent...............................................................: 2.6 MB 14 kB/s




running (3m02.3s), 00/10 VUs, 1164 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  3m0s

# ➜  ProjetSession_LOG430 git:(main) ✗ k6 run --vus 10 --duration **5m** monitoring/load_test.js

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
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0005] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0005] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0006] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0008] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0010] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0302] Load test completed                           source=console
INFO[0302] Total API calls made: undefined               source=console
INFO[0302] Authentication failures: undefined            source=console
INFO[0302] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.05%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=21.6ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.05%


  █ TOTAL RESULTS 

    checks_total.......................: 17660  58.390756/s
    checks_succeeded...................: 99.90% 17643 out of 17660
    checks_failed......................: 0.09%  17 out of 17660

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✗ get products status 200
      ↳  99% — ✓ 1910 / ✗ 5
    ✗ products has data
      ↳  99% — ✓ 1910 / ✗ 5
    ✗ products has pagination
      ↳  99% — ✓ 1910 / ✗ 5
    ✗ store products status valid
      ↳  99% — ✓ 1913 / ✗ 2
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ report valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format

    CUSTOM
    api_calls_total.........................................................: 11743  38.826877/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.05%  7 out of 11743
    login_duration..........................................................: avg=9.078091 min=2.763    med=8.6495 max=20.708 p(90)=15.6998 p(95)=16.70585

    HTTP
    http_req_duration.......................................................: avg=8.98ms   min=1.41ms   med=7.42ms max=66.5ms p(90)=15.82ms p(95)=21.6ms  
      { expected_response:true }............................................: avg=8.98ms   min=1.41ms   med=7.42ms max=66.5ms p(90)=15.82ms p(95)=21.61ms 
    http_req_failed.........................................................: 0.05%  7 out of 11766
    http_reqs...............................................................: 11766  38.902924/s

    EXECUTION
    iteration_duration......................................................: avg=1.57s    min=529.17ms med=1.58s  max=2.62s  p(90)=2.37s   p(95)=2.46s   
    iterations..............................................................: 1915   6.331727/s
    vus.....................................................................: 3      min=3          max=10
    vus_max.................................................................: 10     min=10         max=10

    NETWORK
    data_received...........................................................: 14 MB  46 kB/s
    data_sent...............................................................: 4.3 MB 14 kB/s




running (5m02.4s), 00/10 VUs, 1915 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  5m0s