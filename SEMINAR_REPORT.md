A Report
on
“Design and Implementation of an End-to-End DevOps Pipeline for an E-Governance Application Using GitLab, Docker, Kubernetes, and Prometheus-Grafana Monitoring”
Submitted to the
Savitribai Phule Pune University
In partial fulfillment for the award of the Degree of
Bachelor of Engineering
in
Information Technology 
by
Amit Kangane(BIA27) Ankush Patil(BIA04) Vedant Pimple(BI46) Yash Bankar(BIA45)
Under the guidance of
Prof. Swati Shinde
DEPARTMENT OF INFORMATION TECHNOLOGY
INTERNATIONAL INSTITUTE OF INFORMATION TECHNOLOGY, PUNE - 411057
SAVITRIBAI PHULE PUNE UNIVERSITY
2026 – 2027

CERTIFICATE
This is to certify that the Seminar report entitled “Design and Implementation of an End-to-End DevOps Pipeline for an E-Governance Application Using GitLab, Docker, Kubernetes, and Prometheus-Grafana Monitoring” being submitted by Amit Kangane(BIA27), Ankush Patil(BIA04), Vedant Pimple(BI46) , Yash Bankar(BIA45) is a record of bonafide work carried out by them under the supervision and guidance of Prof. Swati Shinde in partial fulfillment of the requirement for BE (Information Technology) – 2019 course of Savitribai Phule Pune University, Pune in the academic year 2026–2027.
Date: 	 Place: 		
       Prof. Swati Shinde 				              	  Dr. Jyoti V. Surve	 
            Guide						Head of the Department
 
ACKNOWLEDGEMENT
We take this opportunity to express our sincere gratitude to all those who have contributed to the successful completion of this seminar work. First and foremost, we express our deep sense of gratitude to our guide Prof. Swati Shinde, Department of Information Technology, for continuous guidance, valuable suggestions, and constant encouragement throughout the duration of this work.
We are thankful to the Head of the Department and the faculty members of the Department of Information Technology for providing the necessary facilities and a conducive academic environment. We also acknowledge the technical support received from the laboratory staff during the configuration and testing of the DevOps toolchain, container runtimes, and cluster orchestration.
We are grateful to Savitribai Phule Pune University for providing the academic framework under which this seminar has been undertaken. We further acknowledge the open-source communities and maintainers of FastAPI, GitLab CI/CD, Docker, Postman, Newman, Kubernetes, Prometheus, and Grafana, whose documentation and tools formed the practical foundation of this work.
Finally, we express our heartfelt thanks to our families and friends for their moral support and understanding during the course of this seminar.
     Amit Kangane(BIA27)     Ankush Patil(BIA04)    Vedant Pimple(BI46)     Yash Bankar(BIA45)

ABSTRACT
This seminar report presents the design and implementation of an E-Governance Citizen Services Portal developed as a high-concurrency microservice and integrated with modern DevOps practices. The system is built using Python 3.11 and FastAPI, exposing REST endpoints for vital civil records (birth certificates), land registry and mutation, municipal trade licensing, and civic grievance redressal. The development workflow incorporates GitLab CI/CD for end-to-end automation, testing with Pytest and Newman (Postman), Git and GitLab for version control, Docker for multi-stage containerization with non-root security (UID 10001), container registry for image distribution, and Kubernetes for declarative orchestration and rolling zero-downtime deployment.
Observability is achieved through native Prometheus metric exposition on /metrics, Prometheus time-series scraping, Alertmanager rules, and Grafana dashboards that visualize Service Level Agreement (SLA) availability, response latency percentiles (p50, p90, p95, p99), HTTP 5xx error percentages, and container CPU and memory utilization. The report documents the end-to-end workflow from source code to running Kubernetes pods and live telemetry, demonstrating automated build, automated contract testing, continuous deployment, and alert generation during a simulated service failure.
Key results include successful Pytest unit test executions, 8 out of 8 Postman contract and SLA assertions passing via Newman CLI, container image compilation with Trivy vulnerability scanning, Kubernetes Deployment reaching the Running state with 3 replicas, exposure via a Kubernetes Service, successful Prometheus scraping of the target application, creation of a dedicated Grafana operational dashboard, and automated alert firing (EgovServiceDown) with self-healing recovery during chaos injection. The seminar concludes with a discussion of advantages, limitations, practical applications in public sector IT, and directions for future enterprise hardening.

CONTENTS
Table of Contents
CERTIFICATE	2
ACKNOWLEDGEMENT	3
ABSTRACT	4
CONTENTS	5
LIST OF FIGURES	7
LIST OF TABLES	8
CHAPTER 1 INTRODUCTION	9
1.1	Introduction to the Project	9
1.2	Motivation Behind the Project	9
1.3	Aim and Objectives	9
1.4	Introduction to the Seminar Topic	10
1.5	Organization of the Report	10
CHAPTER 2 LITERATURE SURVEY	11
2.1	Introduction	11
2.2	Existing Approaches to Software Delivery and DevOps	11
2.3	CI/CD and Automated Testing	11
2.4	Containerization and Kubernetes	11
2.5	Monitoring with Prometheus and Grafana	12
2.6	Comparative Analysis of Existing Approaches	12
2.7	Research Gaps and Project Relevance	12
CHAPTER 3 SYSTEM ARCHITECTURE AND TECHNOLOGIES	13
3.1	System Overview	13
3.2	Application Architecture	13
3.3	Backend Design and REST APIs	14
3.4	Automated Testing and Build Workflow	15
3.5	GitLab CI/CD Pipeline Design	16
3.6	Docker Containerization	16
3.7	Kubernetes Deployment and Service	16
3.8	Prometheus Metrics Collection	16
3.9	Grafana Dashboard and Visualization	17
CHAPTER 4 IMPLEMENTATION, RESULTS AND APPLICATIONS	18
4.1	Development and Implementation Methodology	18
4.2	Source Code and Version Control	18
4.3	Build and Test Results	18
4.4	Containerization and Image Management	18
4.5	Kubernetes Deployment Results	18
4.6	Monitoring and Observability Results	19
4.7	Advantages and Limitations	19
4.8	Applications and Practical Relevance	19
4.9	Challenges Encountered and Solutions	20
CHAPTER 5 CONCLUSION AND FUTURE SCOPE	21
REFERENCES	22
APPENDIX	23
A.1	Important Commands	23

LIST OF FIGURES
| Sr. No. | Figure Name | Page No. |
| :---: | :--- | :---: |
| 1 | Figure 1.1: Overall System Architecture | 12 |
| 2 | Figure 1.2: End-to-End DevOps CI/CD Workflow | 13 |
| 3 | Figure 3.1: Prometheus and Grafana Monitoring Architecture | 19 |
| 4 | Figure 3.2: Docker and Kubernetes Deployment Architecture | 18 |
| 5 | Figure 3.3: Application Request and Response Flow | 14 |
| 6 | Figure 3.4: Automated Build and Testing Workflow | 15 |

LIST OF TABLES
| Sr. No. | Table Name | Page No. |
| :---: | :--- | :---: |
| 1 | Table 2.1: Comparison of Traditional Delivery vs DevOps Approaches | 10 |
| 2 | Table 3.1: Technology Stack and Responsibilities | 13 |
| 3 | Table 3.2: REST API Endpoints | 14 |
| 4 | Table 4.1: Test Case Summary | 23 |
| 5 | Table 4.2: Implemented, Partial, and Future Features | 26 |
| 6 | Table 4.3: Component Responsibility Matrix | 27 |

CHAPTER 1 INTRODUCTION
1.1 Introduction to the Project
Public sector administrative bodies increasingly rely on software systems to deliver civic entitlements, issue statutory certificates, process commercial trade licenses, and resolve citizen grievances. Traditional e-governance solutions often suffer from manual deployment processes, limited horizontal scalability, unpredictable maintenance downtimes, and opaque operational behaviour. This seminar presents an E-Governance Citizen Portal Application developed as a high-concurrency backend service using Python and FastAPI, together with a complete DevOps toolchain that automates build, test, containerization, deployment, and monitoring.
The application exposes RESTful endpoints for vital civil registration, land title mutation, business licenses, and grievance redressal, designed to run as a containerized microservice. The DevOps pipeline connects source control on GitLab with automated linting, Pytest test suites, Newman-driven Postman API regression testing, Docker multi-stage image creation, Kubernetes zero-downtime deployment, and continuous observability through Prometheus and Grafana. The project therefore serves both as a functional civic domain application and as a practical case study of modern software delivery practices.
The system was implemented with Python 3.11 and FastAPI 0.115. Automated API contract tests employ Postman Collection v2.1 executed headless via Newman. Version control is maintained on Git with structured GitLab CI/CD stages. The Kubernetes deployment was verified to reach the Running state across 3 replicas, the application was exposed via a ClusterIP Service, Prometheus successfully scraped the application target, and a Grafana dashboard named E-Governance Operational Dashboard was created with panels for service availability SLA, response latency percentiles, HTTP error distribution, and container resource utilization.

1.2 Motivation Behind the Project
The motivation for this work arises from two complementary needs. First, civic administrations require reliable software that can process public applications with predictable performance, high data integrity, and strict Service Level Agreements (SLAs). Second, modern software engineering practice has established that frequent, automated, and observable delivery pipelines reduce the risk of defective releases and improve the speed of feedback. Combining these needs yields a project that is both domain-relevant and pedagogically valuable.
Manual software delivery processes in public administration are error-prone and slow. Configuration drift between staging and production environments is a common source of public portal outages. Containerization and orchestration address environment consistency, while continuous integration and automated API testing reduce the time between code changes and validated deployments. Observability tools close the loop by making runtime health visible and triggering automated self-healing during service degradation. The present project was undertaken to apply these practices to a concrete e-governance application and to document the resulting architecture, implementation decisions, and observed outcomes.

1.3 Aim and Objectives
The aim of this project is to design, implement, and demonstrate an E-Governance Citizen Portal Application that is developed, delivered, and monitored using contemporary DevOps practices.
The specific objectives are:
1. To develop a FastAPI application providing REST APIs for citizen services, health probes (/healthz, /ready), and chaos failure testing.
2. To establish an automated test suite using Pytest for unit validation and Postman/Newman for API contract and SLA testing.
3. To containerize the application with a multi-stage Dockerfile adhering to non-root execution (UID 10001) and security best practices.
4. To deploy the containerized application on Kubernetes using declarative manifests (Namespace, Deployment, Service, HPA, Ingress).
5. To instrument the application with native Prometheus metrics and enable scraping via Prometheus server configuration.
6. To formulate Prometheus alerting rules for service availability, high HTTP error rates, and response latency breaches.
7. To create Grafana dashboards visualizing real-time SLA availability, latency percentiles, error rates, and resource utilization.
8. To configure a GitLab CI/CD pipeline orchestrating linting, testing, packaging, API verification, and deployment.
9. To demonstrate automated alert generation, notification dispatch, and self-healing recovery during a simulated service failure.

1.4 Introduction to the Seminar Topic
DevOps is a set of cultural and technical practices that aim to shorten the systems development life cycle while delivering features, fixes, and updates frequently and reliably. Core technical enablers include continuous integration, continuous delivery, infrastructure as code, containerization, orchestration, and observability. This seminar focuses on the practical application of these practices to an e-governance citizen services backend.
Aim and Objectives of the Seminar
The aim of the seminar is to present a coherent account of how DevOps tooling can be applied to a realistic public sector application, covering architecture, implementation, results, and lessons learned. The seminar objectives are to explain the chosen technology stack, document the end-to-end delivery workflow, present verified results, and demonstrate automated incident response during simulated service degradation.

1.5 Organization of the Report
The remainder of this report is organized as follows. Chapter 2 surveys relevant literature on DevOps, CI/CD, containerization, orchestration, and monitoring. Chapter 3 describes the system architecture and the technologies employed. Chapter 4 presents implementation details, results, advantages, limitations, and applications. Chapter 5 concludes the report and outlines future scope. References and an appendix containing commands and configuration snippets follow the main chapters.

CHAPTER 2 LITERATURE SURVEY
2.1 Introduction
This chapter reviews scholarly and authoritative sources related to continuous software engineering practices, container orchestration, and observability. The survey establishes the conceptual foundation for the project and identifies research gaps that the present work addresses in an educational and practical setting.

2.2 Existing Approaches to Software Delivery and DevOps
DevOps emerged as a response to the friction between software development and IT operations teams. Early literature emphasized cultural change, shared ownership of the delivery pipeline, and the automation of repetitive tasks [1]. Systematic reviews have classified DevOps capabilities across the software life cycle, highlighting automation, continuous monitoring, continuous integration, and continuous deployment as central practices [2].
Traditional waterfall or staged delivery models separate development from operations and typically involve infrequent, high-risk releases. In contrast, DevOps-oriented organizations aim for smaller, more frequent releases supported by automated testing and infrastructure provisioning. Empirical studies indicate that adoption of DevOps practices is associated with higher deployment frequency, improved stability, and reduced defect escape rates [2].

2.3 CI/CD and Automated Testing
Continuous Integration (CI), Continuous Delivery, and Continuous Deployment form a spectrum of automation maturity. Shahin et al. conducted a systematic literature review of continuous practices, identifying approaches and tools that reduce build and test time, increase visibility of results, support automated testing, detect faults, and improve the reliability of deployment pipelines [1]. Their review of 69 papers remains a foundational reference for understanding continuous delivery tooling.
Automated API testing through headless runners like Newman ensures contract fidelity and verifies response latency constraints before code is promoted to production clusters [4]. Integrating security scanning tools such as Trivy into CI/CD pipelines shifts vulnerability detection leftward, catching unpatched Common Vulnerabilities and Exposures (CVEs) during the container compilation phase rather than post-deployment [11].

2.4 Containerization and Kubernetes
Containerization packages an application together with its dependencies into a portable unit. Docker has become the de-facto standard for building and distributing container images [5]. Kubernetes, originally developed at Google and now a Cloud Native Computing Foundation (CNCF) graduated project, provides declarative orchestration of containers, including scheduling, scaling, service discovery, health monitoring, and zero-downtime rolling updates [6].
In the context of public sector and municipal governance applications, microservices deployed on Kubernetes enable independent scaling of high-demand citizen services, such as tax filing or certificate issuance, while isolating faults from other municipal services [3].

2.5 Monitoring with Prometheus and Grafana
Observability is essential for operating containerized systems whose topology is dynamic. Prometheus is a pull-based monitoring system that scrapes metrics endpoints over HTTP and stores time-series data in an optimized storage engine [7]. Prometheus Alertmanager evaluates alerting rules against scraped metrics, routing alerts based on grouping and inhibition rules [8]. Grafana provides visual dashboarding on top of Prometheus data sources, enabling operators to analyze Service Level Indicators (SLIs) and resource trends [9].
FastAPI applications expose metrics through the Prometheus Client library, which serves metrics in Prometheus exposition format on a dedicated /metrics route. In Kubernetes, Prometheus scrapes application pods via Service endpoints or ServiceMonitor custom resources, closing the loop between runtime performance and operational visibility.

2.6 Comparative Analysis of Existing Approaches
Table 2.1 summarizes key differences between traditional software delivery and a DevOps-oriented approach as applied in this project.
Table 2.1: Comparison of Traditional Delivery vs DevOps Approaches
| Aspect | Traditional Delivery | DevOps Approach (This Project) |
| :--- | :--- | :--- |
| Release frequency | Infrequent, large releases (quarterly) | Frequent, small releases via GitLab CI/CD |
| Environment consistency | Manual server configuration, drift risk | Docker container images, identical runtime |
| Testing | Late-stage, manual user testing | Automated unit (Pytest) & API tests (Newman) |
| Deployment | Manual scripts, scheduled downtime | Kubernetes rolling updates, zero downtime |
| Observability | Reactive, log inspection after failure | Pull-based Prometheus metrics + Grafana |
| Feedback loop | Long (days to weeks) | Short (minutes: build, test, and scrape cycle)|
| Tooling | Heterogeneous, siloed tools | Integrated: Git, GitLab CI, Docker, K8s, Prom |

2.7 Research Gaps and Project Relevance
While extensive literature exists on individual DevOps practices, educational case studies that document a complete, working pipeline for a domain-specific e-governance application remain valuable. Many published systems focus either on application design or on infrastructure automation in isolation. This seminar bridges the gap by presenting a coherent narrative from civic domain requirements through implementation, containerization, orchestration, and observability, incorporating simulated chaos failure testing to validate alert generation and self-healing.

CHAPTER 3 SYSTEM ARCHITECTURE AND TECHNOLOGIES
3.1 System Overview
The system comprises three logical planes: the application plane (FastAPI microservice), the delivery plane (Git, GitLab CI/CD, Docker, Newman, Kubernetes), and the observability plane (Prometheus, Alertmanager, Grafana). Figure 1.1 illustrates the overall architecture.

+---------------------------------------------------------------------------------------------------+
|                                  PRESENTATION / CITIZEN LAYER                                     |
|             Citizen Web Portal | Mobile App | Open Data Consumer (citizen.egov.gov.in)            |
+---------------------------------------------------------------------------------------------------+
                                                  | (HTTPS)
+---------------------------------------------------------------------------------------------------+
|                                KUBERNETES INGRESS & ROUTING PLANE                                 |
|                       NGINX Ingress Controller -> egov-portal-service:80/8000                     |
+---------------------------------------------------------------------------------------------------+
                                                  |
+---------------------------------------------------------------------------------------------------+
|                                 APPLICATION & MICROSERVICE PLANE                                  |
|         Pod Replicas (x3): Python 3.11 / FastAPI (UID 10001 Non-Root Runtime User)                |
|         - Civil Birth Registration       - Municipal Trade Licensing                              |
|         - Land Mutation Records          - Public Grievance Redressal                             |
|         - /healthz (Liveness Probe)      - /ready (Readiness Probe)                               |
|         - /metrics (Prometheus Exporter) - /api/v1/chaos/* (Chaos Harness)                        |
+---------------------------------------------------------------------------------------------------+
                       |                                                   |
+-----------------------------------------------+   +-----------------------------------------------+
|         CONTINUOUS DELIVERY (CI/CD)           |   |            OBSERVABILITY & SRE PLANE          |
|  - GitLab CI/CD Pipeline (7 Stages)           |   |  - Prometheus Server (Scrapes /metrics @ 5s)  |
|  - Flake8, Yamllint, Hadolint Quality Gates   |   |  - Prometheus Alertmanager (Firing Alerts)    |
|  - Docker Multi-Stage Image Builder           |   |  - Grafana Operational Dashboards             |
|  - Newman Postman Contract & SLA Testing      |   |  - PagerDuty / Slack Webhook Incident Dispatch|
|  - Trivy Container Vulnerability Scanning     |   |  - K8s Horizontal Pod Autoscaler (HPA: 2-10)  |
|  - Kubectl Rolling Update Deployments         |   |                                               |
+-----------------------------------------------+   +-----------------------------------------------+
Figure 1.1: Overall System Architecture

3.2 Application Architecture
The application follows a modular architecture typical of cloud-native REST services. Routers handle HTTP requests, Pydantic schemas validate input payloads, business logic manages application tracking, and an in-memory data store manages persistence. For automated testing, isolated fixtures verify service contracts without external database dependencies.
Table 3.1: Technology Stack and Responsibilities
| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| Language / Runtime | Python 3.11 | Application execution |
| Framework | FastAPI 0.115 | Web, routing, OpenAPI, DI |
| ASGI Server | Uvicorn 0.32 | High-throughput asynchronous server |
| Automated Testing | Pytest & Newman | Unit tests and Postman API contract tests |
| Version Control | Git / GitLab | Source repository and branch management |
| CI Server | GitLab CI/CD | 7-stage automated pipeline orchestration |
| Container Runtime | Docker Engine | Multi-stage image build and execution |
| Image Registry | GitLab Container Registry | Image storage and SHA tagging |
| Security Scanner | Aqua Trivy | Container image CVE vulnerability scan |
| Orchestration | Kubernetes | Deployment, Service, HPA, Ingress |
| Metrics Exporter | Prometheus Client | Expose /metrics counters and histograms |
| Metrics Engine | Prometheus v2.54 | Pull-based scraping and alert evaluation |
| Alert Management | Alertmanager v0.27 | Notification routing and webhook dispatch |
| Visualization | Grafana 11.1 | SLA, latency, and error rate dashboards |

[ Git Repository ] ---> [ 1. Lint: flake8/yamllint ] ---> [ 2. Unit Test: pytest ]
                                                                   |
                                                                   v
[ 5. Security: Trivy ] <--- [ 4. API Test: Newman ] <--- [ 3. Build: Docker ]
        |
        v
[ 6. Deploy: Kubernetes (Rolling Update) ] ---> [ 7. Verify: Prometheus Scrape ]
Figure 1.2: End-to-End DevOps CI/CD Workflow

3.3 Backend Design and REST APIs
The application exposes citizen governance REST endpoints. Verified endpoints include GET /api/v1/services for listing public services, POST /api/v1/applications for submitting certificate and license requests, GET /api/v1/applications/{id} for tracking, and POST /api/v1/grievances for municipal issue reporting. Probes /healthz and /ready provide Kubernetes lifecycle telemetry.

[ Citizen Client ] ---> [ K8s Service / Port 8000 ] ---> [ FastAPI Controller ]
                                                                 |
                                                                 v
[ Domain In-Memory DB ] <--- [ Business Service Layer ] <--- [ Pydantic Validator ]
Figure 3.3: Application Request and Response Flow

Table 3.2: REST API Endpoints
| Method | Path | Purpose | Status |
| :--- | :--- | :--- | :--- |
| GET | /healthz | Kubernetes Liveness Probe | Implemented & Verified |
| GET | /ready | Kubernetes Readiness Probe | Implemented & Verified |
| GET | /metrics | Prometheus metrics scrape endpoint | Implemented & Verified |
| GET | /api/v1/services | List public citizen services | Implemented & Verified |
| POST | /api/v1/applications | Submit citizen application | Implemented & Verified |
| GET | /api/v1/applications/{id} | Retrieve application status | Implemented & Verified |
| POST | /api/v1/grievances | Lodge citizen grievance ticket | Implemented & Verified |
| GET | /api/v1/grievances/{id} | Retrieve grievance status | Implemented & Verified |
| POST | /api/v1/chaos/simulate-crash| Simulate outage (503 on /healthz) | Implemented & Verified |
| POST | /api/v1/chaos/inject-errors | Inject HTTP 500 failure rate | Implemented & Verified |
| POST | /api/v1/chaos/reset | Reset chaos state to healthy | Implemented & Verified |

3.4 Automated Testing and Build Workflow
Pip and Pytest manage application testing. The test suite exercises health probes, Prometheus exposition formats, citizen workflows, and chaos fault recovery. Newman runs the Postman collection against the active service, evaluating response codes, schemas, and SLA latency (< 150ms).

[ Code Change ] ---> [ Flake8 Lint ] ---> [ Pytest Unit Tests ] ---> [ Newman API Tests ] ---> [ Passed Artifact ]
Figure 3.4: Automated Build and Testing Workflow

3.5 GitLab CI/CD Pipeline Design
GitLab CI/CD orchestrates the automated lifecycle across seven stages defined in .gitlab-ci.yml: lint-and-validate, unit-test, docker-build-push, api-test, security-scan, deploy-kubernetes, and verify-monitoring. Each stage must pass before the pipeline advances to subsequent phases, enforcing quality gates.

3.6 Docker Containerization
The application is packaged into a Docker image using a multi-stage Dockerfile. Stage 1 compiles wheel dependencies. Stage 2 copies these packages into a minimal runtime image and configures an unprivileged user (egovuser, UID 10001). The container includes a native HEALTHCHECK instruction verifying /healthz every 15 seconds.

3.7 Kubernetes Deployment and Service
Kubernetes manifests manage the application in the egov-system namespace. A Deployment runs 3 replicas with RollingUpdate strategy (maxSurge: 1, maxUnavailable: 0) and podAntiAffinity. A ClusterIP Service routes traffic, a HorizontalPodAutoscaler scales replicas dynamically between 2 and 10, and an Ingress resource exposes the service on citizen.egov.gov.in.

+-------------------------------------------------------------------------------+
|                            KUBERNETES CLUSTER (egov-system)                   |
|                                                                               |
|  [ Ingress: citizen.egov.gov.in ] ---> [ ClusterIP Service (Port 80/8000) ]   |
|                                                     |                         |
|                       +-----------------------------+--------------------+    |
|                       |                             |                    |    |
|                       v                             v                    v    |
|               [ Pod Replica 1 ]             [ Pod Replica 2 ]    [ Pod Replica 3 ]
|               (Node 1, UID 10001)           (Node 2, UID 10001)  (Node 3, UID 10001)
|               Health: /healthz              Health: /healthz     Health: /healthz
+-------------------------------------------------------------------------------+
Figure 3.2: Docker and Kubernetes Deployment Architecture

3.8 Prometheus Metrics Collection
The application exposes Prometheus-compliant metrics on /metrics. Prometheus server scrapes this endpoint every 5 seconds. Rules evaluate alert conditions including EgovServiceDown (fired when up == 0 or health == 0 for 15s) and EgovHighHttpErrorRate (fired when 5xx errors exceed 10%). Alerts are routed to Alertmanager for webhook dispatch.

[ E-Gov Application Pod ] ---> (Scrape /metrics @ 5s) ---> [ Prometheus Server ]
            |                                                     |
    (Service Expose)                                     (Evaluates Alert Rules)
            |                                                     |
            v                                                     v
   [ Kubernetes Service ]                                [ Alertmanager v0.27 ]
            |                                                     |
            +-----------------------------------> [ Grafana Dashboard UI ]
Figure 3.1: Prometheus and Grafana Monitoring Architecture

3.9 Grafana Dashboard and Visualization
A Grafana dashboard named E-Governance Operational Dashboard was provisioned. Panels include Service Availability Uptime SLA %, Health Status single stat (ONLINE/DOWN), Latency Percentiles (p50, p90, p95 SLA, p99), HTTP Status Code distribution (2xx, 4xx, 5xx), and Container CPU/Memory utilization.

CHAPTER 4 IMPLEMENTATION, RESULTS AND APPLICATIONS
4.1 Development and Implementation Methodology
Development followed an iterative approach. The FastAPI application was developed and tested locally with Pytest. Version control was established on Git. The multi-stage Dockerfile and Kubernetes manifests were authored, followed by the Postman collection and Newman runner. The Prometheus and Grafana observability stack was integrated next. Finally, the GitLab CI/CD pipeline and chaos failure testing harness were executed and validated.

4.2 Source Code and Version Control
The source code repository is organized with modular separation of concerns. Git provides commit tracking, branching, and collaboration. The repository serves as the single source of truth for microservice code, Postman collections, Kubernetes manifests, and monitoring configurations.

4.3 Build and Test Results
The application was built and tested successfully using Pytest and Newman. The Postman test suite executed 8 tests against live endpoints, with all 8 assertions passing and zero failures.
Table 4.1: Test Case Summary
| Test Objective | Input / Condition | Expected Result | Observed Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| Liveness Probe | GET /healthz | HTTP 200, status HEALTHY, < 150ms | HTTP 200, 0.4ms | PASS |
| Readiness Probe | GET /ready | HTTP 200, ready_for_traffic true | HTTP 200, 0.1ms | PASS |
| Prometheus Scrape | GET /metrics | HTTP 200, text/plain, has metrics | HTTP 200, 0.1ms | PASS |
| List Services | GET /api/v1/services | HTTP 200, list >= 3 services | HTTP 200, 0.1ms | PASS |
| Submit Application | POST /api/v1/applications | HTTP 201, APP- ID generated | HTTP 201, 0.3ms | PASS |
| Query Application | GET /api/v1/applications/{id}| HTTP 200, record matches ID | HTTP 200, 0.1ms | PASS |
| Lodge Grievance | POST /api/v1/grievances | HTTP 201, assigned to ward officer | HTTP 201, 0.2ms | PASS |
| Negative Validation | POST /api/v1/applications (bad) | HTTP 400 Bad Request | HTTP 400, 0.1ms | PASS |

4.4 Containerization and Image Management
Multi-stage Docker builds compiled images with optimized layer caching. Security audits confirmed the container runs under non-root UID 10001 with no build compilers present in the runtime image. Trivy vulnerability scans reported zero HIGH or CRITICAL CVEs.

4.5 Kubernetes Deployment Results
The Kubernetes Deployment reached the Running state across 3 replicas. Pods were scheduled across nodes according to podAntiAffinity rules. The ClusterIP Service provided stable load-balanced networking, and rolling updates achieved zero dropped connections.

4.6 Monitoring and Observability Results
Prometheus successfully scraped the egov-portal target, with up{job="egov-portal"} evaluating to 1. Grafana rendered real-time panels displaying 100% service uptime SLA, p95 response latency below 5ms during baseline traffic, and active application processing counters.

4.7 Advantages and Limitations
Advantages include environment consistency through multi-stage Docker images, automated quality gates through Pytest and Newman, zero-downtime deployments with Kubernetes, and proactive observability through Prometheus and Grafana.
Limitations include the use of in-memory storage for demonstration rather than an external database cluster, single-cluster scope, and internal chaos injection rather than kernel-level network partitioning tools.

Table 4.2: Implemented, Partial, and Future Features
| Feature | Status | Notes |
| :--- | :---: | :--- |
| Citizen REST APIs | Implemented | Vital records, land, trade, grievances verified |
| Pytest Unit Tests | Implemented | Health, metrics, and business logic tests pass |
| Newman Postman API Suite | Implemented | 8/8 contract and SLA tests passing |
| Multi-Stage Dockerfile | Implemented | Non-root security user UID 10001 verified |
| Kubernetes Deployment & Service| Implemented | 3 replicas, RollingUpdate, ClusterIP running |
| Prometheus Scraping & Alerts | Implemented | Rules: EgovServiceDown, EgovHighHttpErrorRate |
| Grafana Dashboard | Implemented | Uptime SLA, latency percentiles, error rates |
| Simulated Failure & Self-Healing | Implemented | Verified alert firing and automated pod recovery |
| Production PostgreSQL DB | Future | Replace in-memory store with clustered DB |
| GitOps Delivery (Argo CD) | Future | Declarative GitOps continuous synchronization |
| Service Mesh (Istio) | Future | Mutual TLS and distributed tracing |

4.8 Applications and Practical Relevance
The system demonstrates practices directly applicable to municipal corporations and public administration departments managing citizen portals, licensing platforms, and civic grievance systems.

Table 4.3: Component Responsibility Matrix
| Component | Primary Responsibility | Interacts With |
| :--- | :--- | :--- |
| FastAPI Application | Business logic, citizen REST APIs, metrics | DB, Probes, K8s Service |
| Pytest & Newman | Automated unit and API contract testing | FastAPI service, CI pipeline |
| GitLab CI/CD | Pipeline orchestration (7 stages) | Git, Docker, Newman, K8s |
| Docker | Multi-stage packaging, non-root runtime | GitLab CI, Kubernetes |
| Kubernetes | Scheduling, rolling updates, autoscaling | Docker images, Ingress, Prom |
| Prometheus | Metrics collection, TSDB storage, alerts | App /metrics, Alertmanager |
| Grafana | Visualization of SLA, latency, error rates | Prometheus data source |

4.9 Challenges Encountered and Solutions
Configuring non-root container execution was solved by provisioning user egovuser (UID 10001) in the Dockerfile. Prometheus scrape format alignment was achieved using the official prometheus_client library with text/plain exposition. Dynamic test data propagation in Newman was handled via Postman environment scripts extracting application IDs from response payloads.

CHAPTER 5 CONCLUSION AND FUTURE SCOPE
5.1 Conclusion
This seminar has presented the design and implementation of an E-Governance Citizen Portal Application integrated with modern DevOps practices. The application, built with Python 3.11 and FastAPI, provides functional REST endpoints for civic services. The delivery pipeline incorporates GitLab CI/CD automation, Pytest and Newman testing, multi-stage Docker containerization, Kubernetes rolling deployments, and observability through Prometheus, Alertmanager, and Grafana.
Verified outcomes include 8 out of 8 Postman tests passing, non-root Docker packaging, Kubernetes pods in Running state across 3 replicas, active Prometheus scraping, Grafana SLA visualization, and verified alert generation with self-healing recovery during simulated service failures. The project demonstrates how contemporary DevOps practices establish reliable, repeatable, and observable software delivery for public sector applications.

5.2 Future Scope
Future enhancements include:
1. Integrating GitOps automation using Argo CD or Flux for declarative repository synchronization.
2. Replacing in-memory persistence with an enterprise PostgreSQL cluster and automated database migrations.
3. Incorporating kernel-level chaos engineering tools such as Chaos Mesh for network latency and partition testing.
4. Implementing a service mesh (Istio) for mutual TLS and distributed tracing with Jaeger.
5. Deploying across multi-region Kubernetes clusters for geographical disaster recovery.

REFERENCES
1. M. Shahin, M. A. Babar, and L. Zhu, "Continuous Integration, Delivery and Deployment: A Systematic Review on Approaches, Tools, Challenges and Practices," IEEE Access, vol. 5, pp. 3909–3943, 2017.
2. R. Amaro, R. Pereira, and M. Mira da Silva, "Mapping DevOps capabilities to the software life cycle: A systematic literature review," Information and Software Technology, vol. 165, p. 107342, 2024.
3. P. Rodríguez et al., "Continuous deployment of software intensive products and services: A systematic mapping study," Journal of Systems and Software, vol. 123, pp. 263–291, 2017.
4. Postman Inc., "Newman CLI Documentation and Collection Runner Specification," [Online]. Available: https://learning.postman.com/docs/collections/using-newman-cli/
5. Docker Inc., "Docker Documentation," [Online]. Available: https://docs.docker.com/
6. Kubernetes Authors, "Kubernetes Documentation," Cloud Native Computing Foundation. [Online]. Available: https://kubernetes.io/docs/
7. Prometheus Authors, "Prometheus Documentation," Cloud Native Computing Foundation. [Online]. Available: https://prometheus.io/docs/
8. Prometheus Community, "Alertmanager Notification Routing Architecture," [Online]. Available: https://prometheus.io/docs/alerting/latest/alertmanager/
9. Grafana Labs, "Grafana Documentation," [Online]. Available: https://grafana.com/docs/
10. FastAPI Project, "FastAPI Framework Documentation," [Online]. Available: https://fastapi.tiangolo.com/
11. Aqua Security, "Trivy Vulnerability Scanner Documentation," [Online]. Available: https://aquasecurity.github.io/trivy/
12. GitLab B.V., "GitLab CI/CD Documentation," [Online]. Available: https://docs.gitlab.com/ee/ci/
13. Python Software Foundation, "Python 3 Documentation," [Online]. Available: https://docs.python.org/3/
14. B. C. Pragathi, H. Maddirala, and S. M., "Implementing an Effective Infrastructure Monitoring Solution with Prometheus and Grafana," International Journal of Computer Applications, vol. 186, no. 38, Sept. 2024.
15. GitLab repository: https://gitlab.com/gov-tech/egov-citizen-portal
16. Container registry: registry.gitlab.com/gov-tech/egov-citizen-portal:v1.0.0

APPENDIX
A.1 Important Commands
1. Automated Demo Runner:
python scripts/run_local_demo.py
2. Docker Compose Local Stack:
docker compose up -d --build
3. Newman Standalone API Testing:
newman run postman/egov_citizen_api.postman_collection.json --environment postman/egov_staging.postman_environment.json --reporters cli,junit --reporter-junit-export newman-report.xml
4. Kubernetes Manifest Deployment:
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-deployment.yaml
kubectl apply -f k8s/04-service.yaml
kubectl apply -f k8s/05-hpa.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl rollout status deployment/egov-citizen-portal -n egov-system
5. Failure Simulation & Alert Generation:
python scripts/simulate_failure.py
