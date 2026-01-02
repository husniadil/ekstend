# Question Categories

Deep-dive question templates organized by category. Use these as inspiration - always tailor to the specific context.

## Technical Architecture

### Data Flow & Storage

- "Where does this data originate, and what transformations happen before it reaches the user?"
- "If we needed to audit who changed what and when, does the current design support that?"
- "What happens to this data when a user deletes their account?"
- "Is this data derived from other data, or is it the source of truth? If derived, when should it recompute?"

### Integration Points

- "What existing systems does this need to read from or write to?"
- "If [external service] has a 5-second latency spike, how should this feature behave?"
- "Are there webhooks, callbacks, or events we need to emit for other systems to consume?"
- "What's the contract with [integration]? Is it documented? Can it change?"

### Performance & Scale

- "What's the expected p50/p99 latency for this operation?"
- "If this runs 100x more than expected, what breaks first?"
- "Is this a hot path that runs on every request, or a cold path that runs occasionally?"
- "What's the read-to-write ratio? 100:1? 1:1? 1:100?"

## Edge Cases & Failure Modes

### Partial Failures

- "If step 3 of 5 fails, what's in a consistent state and what isn't?"
- "Can users resume from where they left off, or must they start over?"
- "What if the database write succeeds but the notification email fails?"
- "How do we detect and recover from a half-completed operation?"

### Race Conditions

- "What if two users edit the same [resource] within the same second?"
- "If a user opens this in two tabs and submits from both, what happens?"
- "What if the background job processes a record that was just deleted?"
- "Is there a TOCTOU (time-of-check-time-of-use) vulnerability here?"

### Boundary Conditions

- "What's the largest [input] we should realistically support? What happens just past that?"
- "What if the list is empty? What if it has one item? What if it has millions?"
- "What happens at midnight? At month-end? At year-end? On February 29?"
- "What if the user's timezone changes mid-operation?"

### Malicious Input

- "What if someone deliberately sends malformed data?"
- "How do we prevent abuse of this feature (spam, scraping, DoS)?"
- "What's the blast radius if an attacker gains access to this endpoint?"
- "Are there rate limits? What's the appropriate limit?"

## Trade-offs & Priorities

### Consistency vs Availability

- "If we can't reach the database, should this fail fast or return stale data?"
- "Is it acceptable for two users to briefly see different versions of this data?"
- "How long can we cache this before staleness becomes a problem?"

### Flexibility vs Simplicity

- "Are we building a general solution or solving this specific case?"
- "Who needs to configure this? Developers? Admins? End users?"
- "Is it worth adding [flexibility] if it adds [complexity]?"
- "Will requirements here change frequently, or is this stable?"

### Speed vs Safety

- "Should we validate exhaustively, or trust the upstream source?"
- "Is optimistic UI worth the complexity of rollback scenarios?"
- "Can we ship with basic validation and tighten later, or must it be bulletproof day one?"

## UX & User Journeys

### User Mental Model

- "What does the user think they're doing vs what's actually happening?"
- "What terminology does the user use for this concept?"
- "What would confuse a user encountering this for the first time?"
- "What expectations is the user bringing from similar products?"

### Error Recovery

- "How does the user know something went wrong?"
- "What actions can they take to recover? Is it obvious?"
- "Do we explain why it failed, or just that it failed?"
- "Can the user retry? Should they wait? Should they contact support?"

### Progressive Disclosure

- "What's the simplest version a new user needs?"
- "What power-user features should be hidden until needed?"
- "How does the user discover advanced capabilities?"

### Accessibility

- "Can this be operated with keyboard only?"
- "What does a screen reader announce for this interaction?"
- "Are there color contrast or motion sensitivity concerns?"
- "Does this work at 200% zoom?"

## Security & Compliance

### Authorization

- "Who should be able to do this? Who should NOT?"
- "Can permissions change while the user is mid-operation?"
- "What happens if someone bookmarks a URL they later lose access to?"
- "Are there admin backdoors? How are they protected?"

### Data Protection

- "What's the sensitivity level of this data (PII, financial, health)?"
- "Where is this data logged? Should it be masked?"
- "How long should this data be retained? When must it be deleted?"
- "Who has access to this data in production?"

### Audit & Compliance

- "Do we need to log who accessed this and when?"
- "Are there regulatory requirements (GDPR, HIPAA, SOC2)?"
- "Can we prove compliance if audited?"

## Operations & Observability

### Deployment

- "How do we deploy this? Can we roll back?"
- "Is there a feature flag? Who controls it?"
- "What's the rollout plan? Percentage? Canary? Big bang?"
- "What happens to in-flight requests during deployment?"

### Monitoring

- "How do we know this is working correctly in production?"
- "What metrics should we track? What alerts should we set?"
- "What does 'unhealthy' look like for this feature?"
- "How would we detect a silent failure?"

### Debugging

- "What information do we need to debug issues?"
- "Can we trace a request through all components?"
- "How do we reproduce production issues locally?"
- "What are the likely failure modes to watch for?"

## Domain-Specific

### For Frontend Work

- "What's the component hierarchy? Where does state live?"
- "How does this behave on mobile vs desktop?"
- "What happens during slow network conditions?"
- "Are there animations or transitions? What triggers them?"

### For Backend/API Work

- "What's the API shape? REST? GraphQL? RPC?"
- "How do we version this API? What's the deprecation policy?"
- "What's in the request/response? Are there optional fields?"
- "How do we handle pagination? Filtering? Sorting?"

### For Database Work

- "What indexes do we need? Have we tested with realistic data volumes?"
- "Are there foreign key constraints? What's the cascade behavior?"
- "How do we migrate existing data? Is it backward compatible?"
- "What's the backup and recovery story?"

### For Infrastructure Work

- "What resources does this need? CPU? Memory? Network? Disk?"
- "How does this scale? Horizontally? Vertically?"
- "What's the cost model? Is there a budget?"
- "What's the disaster recovery plan?"
