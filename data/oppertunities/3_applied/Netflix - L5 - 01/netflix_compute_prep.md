# Netflix Compute Control Plane Interview Prep

## Interview Process

Same as ML role:
1. Recruiter (30 min)
2. Hiring manager (45-60 min)
3. Technical deep dive (60-90 min)
4. Cross-functional partners (45-60 min)
5. Culture (45-60 min)
6. Team rounds (2-3 x 45-60 min)

---

## Your Main Story

"I'm currently leading Kubernetes migration at Walmart while building platform services that handle internet-scale traffic. My focus has been on making reliable, scalable infrastructure that other engineers can depend on - they write features, I handle the platform. I'm hands-on with containers right now, learning K8s deeply, and I want to take that to Netflix scale where you're managing millions of containers."

---

## Key Talking Points

### 1. Kubernetes & Container Platform Experience

**What you're doing NOW:**
- Leading WCNP (Walmart Cloud Native Platform) migration
- Hands-on: Dockerfiles, K8s manifests, Helm charts, debugging pods
- Real challenges: stateful services, service discovery, secrets, observability
- Building tooling to make container deployment self-service

**Be honest about timeline:**
- "I'm in year 1-2 of this journey, not year 5"
- "I'm learning by doing - migrating actual production services"
- "The fundamentals are clicking, now I want to go deeper at Netflix scale"

**Questions they'll ask:**
- "How deep is your K8s experience?" → Honest: "I'm actively learning. I've containerized X services, debugged Y pod issues, built Z tooling. Not an expert yet, but progressing fast."
- "What K8s challenges have you hit?" → Service discovery, secret rotation, stateful workloads, resource limits, debugging crashloops
- "How do you handle K8s upgrades?" → Still learning this, but understand the challenges: API deprecations, workload disruption, testing strategy

### 2. Platform Engineering (Engineers as Customers)

**What you built:**
- Team Portal: 50+ engineer customers, self-service deployments
- 60% reduction in time-to-production
- Philosophy: engineers write logic, platform handles infrastructure
- Centralized secrets, logging, monitoring

**Why this matters:**
Netflix wants "set it and forget it" - same thing you've built.

**Questions they'll ask:**
- "How do you design self-service platforms?" → Start with user pain points, build abstractions that hide complexity, provide escape hatches for power users
- "How do you measure platform success?" → Adoption rate, time-to-production, support ticket volume, user satisfaction
- "How do you handle platform feedback?" → Regular syncs with users, feedback loops, prioritize based on impact

### 3. Tier0 Operational Excellence

**What you've done:**
- All systems run at 99.99% uptime (4 min/month downtime)
- Comprehensive observability: metrics, logs, traces, alerts
- On-call rotation, post-mortems, runbooks
- Design for failure from day one

**Why this matters:**
Netflix Compute is Tier0 - if it's down, Netflix is down.

**Questions they'll ask:**
- "How do you ensure 99.99% uptime?" → Multi-region, health checks, circuit breakers, gradual rollouts, automated rollback
- "Tell me about a major incident" → Pick one from Walmart, walk through: detection, triage, mitigation, root cause, prevention
- "How do you prevent cascading failures?" → Bulkheads, rate limiting, circuit breakers, graceful degradation, load shedding

### 4. Distributed Systems at Scale

**What you've built:**
- Systems processing millions of events/second
- Multi-region orchestration (4 markets)
- Kafka event-driven architectures
- Horizontal scaling for 10x traffic (Black Friday)

**Why this matters:**
Netflix scale requires distributed systems thinking.

**Questions they'll ask:**
- "How do you handle scale?" → Horizontal scaling, partitioning, caching, async processing, eventual consistency where acceptable
- "How do you debug distributed systems?" → Distributed tracing, correlation IDs, centralized logging, metrics aggregation
- "How do you handle state?" → Minimize state, externalize to data stores, use event sourcing patterns

### 5. Multi-Region / Capacity Management

**What you've done:**
- Multi-region deployment across 4 markets
- Automated orchestration with rollback
- Resource optimization and monitoring

**What you haven't done:**
- Capacity planning at hundreds-of-millions scale
- Hybrid cloud/on-prem orchestration

**How to position:**
- "I've done multi-region orchestration, but not at Netflix spend levels"
- "I haven't done hybrid cloud/on-prem, but I understand the coordination challenges"
- "This is exactly what I want to learn - capacity management at massive scale"

---

## Addressing Your Gaps

### Gap: "Your K8s experience is relatively new"

**What to say:**
"True - I'm in year 1-2 of hands-on Kubernetes work, not year 5. But I'm learning by doing: migrating production services, debugging real issues, building tooling. The fundamentals are solid. What I bring is deep distributed systems thinking from years of building at scale. K8s is a tool - the principles underneath are what matter. I'm confident I can ramp up quickly at Netflix, especially learning from experts."

### Gap: "You haven't done hybrid cloud/on-prem"

**What to say:**
"Correct - my experience has been cloud-only (Azure, AWS). But I've done multi-region orchestration with similar coordination challenges: different configurations, network constraints, state synchronization. Hybrid adds complexity, but the distributed systems patterns are familiar. This is exactly the kind of hard problem I want to tackle."

### Gap: "Capacity management at Netflix scale"

**What to say:**
"My experience has been more application/platform focused than capacity planning. I haven't managed hundreds of millions in compute spend. But I understand resource optimization, cost efficiency, and how to build systems that scale horizontally. I want to learn capacity management at this scale - it's a different level of thinking."

---

## Behavioral Stories

### "Tell me about driving a large initiative"

**Story: WCNP Kubernetes Migration**
- Situation: Walmart needed to modernize infrastructure, containerize services
- My role: Technical lead for migration strategy and execution
- Approach: Assessment → containerization → deployment → monitoring, built tooling for self-service
- Challenges: Stateful services, team education, operational changes
- Outcome: Successfully migrating services, building momentum, creating reusable patterns
- Still ongoing, but showing progress and impact

### "Tell me about platform engineering"

**Story: Team Portal**
- Situation: Engineers spending too much time on infrastructure instead of features
- My approach: Built self-service platform abstracting complexity
- Design: Engineers write logic, platform handles deployment/secrets/logging
- Impact: 60% reduction in time-to-production, high adoption
- Lesson: Platform engineering is about enabling others, not building features

### "Tell me about maintaining reliability"

**Story: 99.99% Uptime Systems**
- All my systems at Walmart run at this SLA
- How: Built-in monitoring, automated alerts, runbooks, gradual rollouts, automated rollback
- Example: Account Risk API - millions of requests/day, p99 <50ms, 99.99% uptime
- Philosophy: Reliability isn't luck, it's design decisions and operational rigor

---

## Netflix Culture Questions

### Freedom & Responsibility
"At Walmart, I've had full ownership of architecture decisions for WCNP migration and platform services. Leadership trusts me to choose tech stacks, design systems, set direction. Risk: if I'm wrong, it impacts many teams. Outcome: Systems running reliably, teams adopting platform. Freedom works because I balance it with accountability - I own the outcomes."

### Candor
"During WCNP migration planning, a senior engineer proposed an approach I thought was too risky. I told them directly: 'This could cause major downtime if we migrate too fast.' They disagreed. I presented data on similar migrations, risk analysis. We compromised on a phased approach. Now we're migrating incrementally with minimal incidents. Candor with data and respect."

### Innovation
"I'm a top 2% Cursor AI user - I adopt new tech when it solves problems. At Walmart, I pioneered LLM-assisted development, increasing team productivity 40%. For K8s, I'm learning from the community, reading Netflix blog posts, experimenting with new patterns. I stay current but pragmatic - adopt what works, not what's hype."

### Context, Not Control
"My Team Portal gives engineers full control over deployments. I don't review every change - I provide context through docs, guardrails, monitoring. If an engineer isn't sure about a deployment, I ask questions: 'What's the blast radius? How will you monitor? What's your rollback plan?' They figure it out. My job is enabling good decisions, not making every decision."

---

## System Design Questions

### "Design a container orchestration system"

**Clarify requirements:**
- Scale? Thousands vs millions of containers?
- Workload types? Stateless, stateful, batch, streaming?
- Multi-region? Multi-cloud? On-prem?
- Latency requirements for scheduling?

**High-level design:**
- Control plane: API server, scheduler, controller manager
- Data plane: Container runtime, networking, storage
- Scheduler: Resource allocation, bin packing, affinity/anti-affinity
- Networking: Service mesh, load balancing, DNS
- Monitoring: Metrics, logs, traces, alerts

**Deep dives:**
- How scheduler makes placement decisions
- How to handle node failures
- How to do rolling updates without downtime
- How to monitor container health

**Your edge:** "I'm learning K8s architecture right now at Walmart - let me walk through what I've learned and where I'd want to go deeper."

### "How do you handle capacity management?"

**Approach:**
- Demand forecasting: historical trends, growth projections, traffic patterns
- Resource allocation: bin packing, oversubscription strategies, reserved capacity
- Cost optimization: spot instances, right-sizing, idle resource detection
- Monitoring: utilization metrics, cost per workload, efficiency dashboards
- Automation: auto-scaling, capacity alerts, budget enforcement

**Be honest:** "I haven't done this at Netflix scale. My experience is smaller. But I understand the principles and I'm excited to learn."

### "Design a hybrid cloud/on-prem orchestration system"

**Challenges:**
- Different APIs and capabilities across platforms
- Network latency and reliability between locations
- Data locality and compliance requirements
- Cost optimization across different pricing models
- Consistent tooling and operational experience

**Design:**
- Unified control plane abstracting platform differences
- Workload placement based on requirements (latency, cost, compliance)
- Data replication and synchronization strategies
- Network overlay for consistent connectivity
- Monitoring and observability across all platforms

**Your honesty:** "I haven't built this, but I've thought about the challenges from my multi-region work. I'd love to learn from Netflix's approach."

---

## Questions to Ask Them

**For hiring manager:**
1. What are the biggest technical challenges for Compute Control Plane right now?
2. How do you see hybrid cloud/on-prem orchestration evolving at Netflix?
3. What does success look like in first 6 months for this role?
4. How does Compute team work with other infrastructure teams?

**For team members:**
1. What's the most interesting technical problem you've worked on recently?
2. How do you balance operational work vs building new capabilities?
3. What's the on-call experience like? How often do incidents happen?
4. What's the best part about working on Compute at Netflix?

**For everyone:**
1. How does Netflix's freedom & responsibility culture show up day-to-day?
2. What kind of person succeeds on this team?

---

## Compensation

**Netflix range:** $100,000 - $720,000 (wider than ML role)

**Your target:** $300K - $500K+ total comp

**What to say:** Same as ML role - emphasize flexibility, focus on impact over number

---

## Final Mindset

**Be honest about where you are:**
- You're NOT a K8s expert with 5 years at scale
- You ARE actively learning K8s through real migration work
- You HAVE deep platform engineering and distributed systems experience
- You're EXCITED to go deeper at Netflix scale

**Your strengths:**
- Platform engineering mindset
- Operational excellence (99.99% uptime)
- Distributed systems thinking
- Cross-functional leadership
- Fast learner (top 2% AI adopter)

**Your gaps:**
- K8s depth (learning now)
- Hybrid cloud/on-prem (new)
- Netflix-scale capacity management (new)

**The pitch:**
"I'm in the middle of a K8s journey with strong platform engineering fundamentals. I'm not the expert who's done this for years, but I'm the person who learns fast, cares about reliability, and wants to build platforms that enable others. I want to take my platform thinking to Netflix scale."

---

## Critical Reminder

This role is a STRETCH compared to the ML Data Products role. Your K8s experience is newer, the hybrid cloud/on-prem is unknown territory. But if you're honest about where you are and show excitement to learn, it could work.

Be authentic. Be curious. Show you're coachable.

Good luck! 🚀