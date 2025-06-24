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
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0008] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0011] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0060] Load test completed                           source=console
INFO[0060] Total API calls made: undefined               source=console
INFO[0060] Authentication failures: undefined            source=console
INFO[0060] Cached tokens: 0                              source=console


  █ THRESHOLDS 

    auth_failures
    ✓ 'rate<0.02' rate=0/s

    errors
    ✓ 'rate<0.1' rate=0.25%

    http_req_duration
    ✓ 'p(95)<2000' p(95)=21.57ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.25%


  █ TOTAL RESULTS 

    checks_total.......................: 3614   59.459835/s
    checks_succeeded...................: 99.55% 3598 out of 3614
    checks_failed......................: 0.44%  16 out of 3614

    ✓ login status 200
    ✓ login has token
    ✓ login response valid
    ✓ health check status 200
    ✓ health check has message
    ✗ get products status 200
      ↳  98% — ✓ 382 / ✗ 5
    ✗ products has data
      ↳  98% — ✓ 382 / ✗ 5
    ✗ products has pagination
      ↳  98% — ✓ 382 / ✗ 5
    ✗ store products status valid
      ↳  99% — ✓ 386 / ✗ 1
    ✓ search products valid response
    ✓ get orders valid response
    ✓ store orders valid response
    ✓ report valid response
    ✓ restock valid response
    ✓ metrics accessible
    ✓ metrics format

    CUSTOM
    api_calls_total.........................................................: 2369   38.9763/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.25%  6 out of 2369
    login_duration..........................................................: avg=12.339682 min=2.29     med=12.9925 max=31.669  p(90)=21.265  p(95)=21.9855

    HTTP
    http_req_duration.......................................................: avg=9.41ms    min=1.43ms   med=7.97ms  max=68.53ms p(90)=16.48ms p(95)=21.57ms
      { expected_response:true }............................................: avg=9.4ms     min=1.43ms   med=7.96ms  max=68.53ms p(90)=16.48ms p(95)=21.58ms
    http_req_failed.........................................................: 0.25%  6 out of 2392
    http_reqs...............................................................: 2392   39.354711/s

    EXECUTION
    iteration_duration......................................................: avg=1.56s     min=537.06ms med=1.59s   max=2.57s   p(90)=2.35s   p(95)=2.45s  
    iterations..............................................................: 387    6.367171/s
    vus.....................................................................: 10     min=10        max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 2.7 MB 44 kB/s
    data_sent...............................................................: 867 kB 14 kB/s




running (1m00.8s), 00/10 VUs, 387 complete and 0 interrupted iterations
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
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0003] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0004] ✓ Authentication successful for user employee (store: 1)  source=console
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
    ✓ 'p(95)<2000' p(95)=20.87ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 10687   58.691524/s
    checks_succeeded...................: 100.00% 10687 out of 10687
    checks_failed......................: 0.00%   0 out of 10687

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
    api_calls_total.........................................................: 7094   38.959266/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 7094
    login_duration..........................................................: avg=13.661273 min=2.237    med=15.9035 max=23.41   p(90)=22.4873 p(95)=23.32565

    HTTP
    http_req_duration.......................................................: avg=9.06ms    min=1.19ms   med=7.82ms  max=51.89ms p(90)=16.11ms p(95)=20.87ms 
      { expected_response:true }............................................: avg=9.06ms    min=1.19ms   med=7.82ms  max=51.89ms p(90)=16.11ms p(95)=20.87ms 
    http_req_failed.........................................................: 0.00%  0 out of 7117
    http_reqs...............................................................: 7117   39.085578/s

    EXECUTION
    iteration_duration......................................................: avg=1.56s     min=529.82ms med=1.55s   max=2.64s   p(90)=2.35s   p(95)=2.46s   
    iterations..............................................................: 1159   6.365068/s
    vus.....................................................................: 1      min=1         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 7.9 MB 44 kB/s
    data_sent...............................................................: 2.6 MB 14 kB/s




running (3m02.1s), 00/10 VUs, 1159 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  3m0s

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
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0000] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0001] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
INFO[0002] ✓ Authentication successful for user manager (store: 0)  source=console
INFO[0002] ✓ Authentication successful for user employee (store: 1)  source=console
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
    ✓ 'p(95)<2000' p(95)=20.52ms

    http_req_failed
    ✓ 'rate<0.05' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 17702   58.762754/s
    checks_succeeded...................: 100.00% 17702 out of 17702
    checks_failed......................: 0.00%   0 out of 17702

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
    api_calls_total.........................................................: 11773  39.081115/s
    auth_failures...........................................................: 0      0/s
    errors..................................................................: 0.00%  0 out of 11773
    login_duration..........................................................: avg=13.013364 min=2.293    med=14.837 max=20.644  p(90)=20.4104 p(95)=20.50935

    HTTP
    http_req_duration.......................................................: avg=9.2ms     min=1.3ms    med=7.95ms max=57.52ms p(90)=16.29ms p(95)=20.52ms 
      { expected_response:true }............................................: avg=9.2ms     min=1.3ms    med=7.95ms max=57.52ms p(90)=16.29ms p(95)=20.52ms 
    http_req_failed.........................................................: 0.00%  0 out of 11796
    http_reqs...............................................................: 11796  39.157465/s

    EXECUTION
    iteration_duration......................................................: avg=1.56s     min=534.63ms med=1.55s  max=2.59s   p(90)=2.36s   p(95)=2.45s   
    iterations..............................................................: 1923   6.383503/s
    vus.....................................................................: 3      min=3          max=10
    vus_max.................................................................: 10     min=10         max=10

    NETWORK
    data_received...........................................................: 14 MB  45 kB/s
    data_sent...............................................................: 4.3 MB 14 kB/s




running (5m01.2s), 00/10 VUs, 1923 complete and 0 interrupted iterations
default ✓ [===============================