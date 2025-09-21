# api-gateway Service
Here is a detailed plan to finish the api-gateway service from top to bottom given that:

- Google OAuth is for user login/authentication.
- GitHub OAuth is for login plus access to user repositories to analyze for the roadmap generation.
- LinkedIn data access is done by headless browser scraping their public profile links (not OAuth).
- MongoDB Atlas is used with connection strings in your `.env`.

***

### What needs to be done in API Gateway stepwise:

1. **Complete OAuth for GitHub and Google (Login + Profile Fetch):**
   - Ensure the GitHub OAuth flow fetches user info and repos, sends user data to AI Guidance for repo analysis.
   - Confirm Google OAuth flow fully supports login and profile fetch.
   - Add proper error handling, token expiration, and refresh mechanisms.
   - Support token blacklist for logout.

2. **Integrate LinkedIn Scraper Endpoint:**
   - Create an API endpoint that accepts a LinkedIn public profile URL.
   - Forward this URL to a headless browser scraper microservice.
   - Receive structured scraped profile data, store or forward to AI Guidance for analysis.
   - Secure and rate-limit this endpoint.

3. **Proxy & Route All AI Guidance & Microservice APIs:**
   - Complete and test proxy routes (`/users/profile`, `/ai/analyze-resume`, `/ai/chat`, etc.) for all services.
   - Implement robust error handling and caching via Redis.
   - Add missing routes for any uncovered APIs needed by frontend.

4. **File Upload Endpoint:**
   - Ensure file upload via multer works correctly and securely.
   - Proxy uploaded resume or portfolio files to Portfolio service.
   - Add validation for file types and sizes.

5. **WebSocket Server:**
   - Validate WebSocket handling for real-time updates if used.
   - Add authentication for WebSocket clients.
   - Add handling for common message types (ping, subscribe, notifications).

6. **Security and Middleware:**
   - Audit and fix all CORS issues.
   - Harden JWT auth middleware (blacklist token checking, renewal).
   - Add rate limiters carefully to protect routes.
   - Setup session store correctly with MongoDB Atlas config from `.env`.

7. **Health Checks:**
   - Ensure `/health` endpoint correctly aggregates microservice health.
   - Add monitoring hooks if needed.

8. **Testing & Documentation:**
   - Write integration tests for all OAuth flows.
   - Write tests for proxy routes, file uploads, and linked scraper routes.
   - Document all routes, auth flows, and environment requirements.

***

### Summary

- OAuth flows (GitHub for repos + Google for login) need to be finished and tested.
- Add headless LinkedIn scraping via a new secure API endpoint.
- Complete proxy routing and add error, rate limiting, and caching.
- Confirm file uploading and forwarding.
- Harden WebSocket and middleware security.
- Create health checks and comprehensive tests.
- Document the API Gateway thoroughly referencing `.env` config like MongoDB Atlas URL.

***

If needed, I can help start generating the code or detailed steps for LinkedIn scraping API, or assist testing/finishing GitHub OAuth integration next.

Based on the project structure and the newly attached AI Guidance service files, here are the **missing features** that need to be implemented:

## Major Missing Features:

### 1. **LinkedIn Profile Scraping Service**
- **Missing:** Dedicated service to scrape LinkedIn public profiles using headless browser
- **Should be:** A separate microservice or integration in AI Guidance to fetch LinkedIn data
- **Current gap:** Only GitHub OAuth exists, no LinkedIn data collection

### 2. **Career Atlas Service Implementation**
- **Missing:** Full career domain/role data service logic
- **Current state:** Only skeleton files (`requirements.txt` and `main.py` stub)
- **Should include:** Career domains, job roles, skill mappings, market trends data

### 3. **Gamification Service**
- **Missing:** Complete gamification logic 
- **Current state:** Only README file
- **Should include:** Points system, badges, leaderboards, challenges, user progress tracking

### 4. **Portfolio Service**
- **Missing:** Portfolio management logic
- **Current state:** Only skeleton files
- **Should include:** Project showcasing, achievements, portfolio templates, proof validation

### 5. **Notification Service**
- **Missing:** Notification management system
- **Current state:** Only skeleton files  
- **Should include:** Email/push notifications, preferences, notification history

### 6. **Simulation/Mock Interview Service**
- **Missing:** Mock interview and simulation logic
- **Current state:** Only skeleton files
- **Should include:** Interview simulations, coding challenges, behavioral assessments

### 7. **Roadmap Generation Logic**
- **Missing:** Complete roadmap generation in AI Guidance
- **Current state:** Basic user input collection exists
- **Should include:** AI-powered career path recommendations, skill gap analysis, learning resources

### 8. **GitHub Repository Analysis**
- **Missing:** Deep GitHub repo analysis for skill assessment
- **Current state:** OAuth setup exists but no analysis logic
- **Should include:** Code quality analysis, technology stack detection, contribution patterns

### 9. **Integration Between Services**
- **Missing:** Service-to-service communication
- **Current state:** API Gateway has proxy routes but services are mostly empty
- **Should include:** Data sharing, coordinated user experiences

### 10. **Frontend Applications**
- **Missing:** Complete frontend implementations
- **Current state:** Only directory structure exists
- **Should include:** Dashboard UI, mobile app, user interfaces for all features

### 11. **Data Analytics & Insights**
- **Missing:** User behavior analytics, career trend analysis
- **Should include:** Usage metrics, success tracking, market insights

### 12. **Testing Infrastructure**
- **Missing:** Comprehensive test suites
- **Current state:** Empty test directories
- **Should include:** Unit tests, integration tests, API tests

## Immediate Priority Implementation Order:

1. **Complete AI Guidance roadmap generation**
2. **Build LinkedIn scraping service**  
3. **Implement Career Atlas with job market data**
4. **Add GitHub repository analysis**
5. **Build basic frontend dashboard**
6. **Implement gamification system**
7. **Add portfolio and notification services**

The foundation is solid with AI Guidance service having proper structure, but most other microservices need complete implementation.


# AI Guidance Service – TODO List

**1. Configuration & Environment**  
- Migrate `config.py` to use Pydantic’s `BaseSettings` for automatic validation and multi-environment support.  
- Enforce presence of required environment variables (OAuth keys, database URLs).  
- Add type annotations for settings (e.g., `JWT_EXPIRATION_MINUTES: int`).  

**2. Dependencies & Tooling**  
- Extend `requirements.txt` with  
  - Testing: `pytest`, `pytest-cov`  
  - Linting: `flake8`, `mypy`  
  - Observability: `prometheus_client`, `opentelemetry-sdk`  
- Add `tox.ini` or `pre-commit` for consistent code quality checks.  

**3. Authentication & Security**  
- Implement JWT revocation via Redis blacklist and enforce TTL.  
- Add `/auth/refresh` endpoint with rotating refresh tokens.  
- Complete GitHub OAuth flow: callback endpoint, token exchange, user storage.  
- Enforce per-endpoint rate limiting using Redis-backed middleware.  
- Configure CORS origins from `ALLOWED_ORIGINS` environment variable.  

**4. Core Services & Endpoints**  
- Build `RoadmapBuilder` service and expose `POST /roadmap/generate`.  
- Implement `GitHubService`  
  - Fetch repo metadata, commit history, language breakdown.  
  - Analyze code quality and contribution patterns.  
- Implement `LinkedInService`  
  - Headless browser scraper (e.g., Playwright) with proxy rotation.  
  - Extract experience, skills, education into structured model.  
- Extend `endpoints.py` with new routes for GitHub & LinkedIn ingestion.  

**5. Business Logic Enhancements**  
- Persona Wizard  
  - Enforce step order and field validation via Pydantic validators.  
  - Abstract scoring logic into plugin classes.  
- Psychometrics  
  - Make scoring algorithms configurable and data-driven.  
- Resume Parsing  
  - Add structured NER extraction for skills, education, experience.  
  - Implement error handling, retries, and fallback OCR pipeline.  
- GenAI Client  
  - Wrap in Redis caching keyed by input hash.  
  - Add timeout, retry, and exponential backoff logic.  
  - Instrument latency and error metrics with Prometheus.  

**6. Data Models & Persistence**  
- Define new Pydantic models and MongoDB collections:  
  - `Repository`, `LinkedInProfile`, `Roadmap`, `RoadmapProgress`  
- Extend `crud.py` with CRUD operations for new entities.  
- Add revision history for roadmap progress tracking.  

**7. Testing & CI**  
- Write unit tests for each service module: parser, scoring, AI client.  
- Create integration tests for endpoint workflows: persona → psychometric → roadmap.  
- Configure CI pipeline (GitHub Actions) to run tests, linting, and coverage checks.  

**8. Observability & Logging**  
- Enhance `logging.py` to emit structured JSON logs with correlation IDs.  
- Add middleware to inject request-level context (request ID, user ID).  
- Expose a Prometheus `/metrics` endpoint and instrument critical code paths.  

**9. Documentation & API Specs**  
- Annotate all endpoints with OpenAPI metadata and example payloads.  
- Serve Swagger UI at `/docs` and Redoc at `/redoc`.  
- Update README with contribution guidelines and architecture overview.  
- Maintain a CHANGELOG and define semantic versioning policy.  

**10. Docker & Deployment**  
- Add health-check endpoint in `main.py` for container orchestration.  
- Extend Dockerfile with non-root user creation and multi-stage build.  
- Include readiness and liveness probes in Kubernetes manifests (if applicable).  
- Update `docker-compose.yml` with mock LinkedIn and GitHub services for local dev.  

***

Completing these tasks will deliver a robust, secure, and production-ready AI Guidance service capable of delivering personalized career roadmaps.