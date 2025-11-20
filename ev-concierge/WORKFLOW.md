# 🔄 EV Concierge Workflow

## Complete Agent Workflow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Gradio UI
    participant Coord as Coordinator Agent
    participant Trip as Trip Planning Agent
    participant Charge as Charging Agent
    participant Amen as Amenities Agent
    participant Pay as Payment Agent
    participant Mon as Monitoring Agent
    participant APIs as External APIs

    User->>UI: "Going to LA tomorrow, battery at 40%"
    UI->>Coord: Parse request & initiate workflow
    
    Note over Coord: Step 1: Trip Analysis
    Coord->>Trip: Analyze trip requirements
    Trip->>APIs: Get route info & weather
    APIs-->>Trip: Distance: 280mi, Weather: 75°F
    Trip->>Trip: Calculate energy needs
    Trip-->>Coord: Needs charging: 65% required, 40% current
    
    Note over Coord: Step 2: Find Charger
    Coord->>Charge: Find optimal charger
    Charge->>APIs: Search EVgo, ChargePoint, Tesla
    APIs-->>Charge: 3 chargers found
    Charge->>Charge: Compare price, speed, location
    Charge->>APIs: Reserve best option (EVgo 350kW)
    APIs-->>Charge: Reservation confirmed
    Charge-->>Coord: Reserved: Tejon Ranch, 10:00 AM
    
    Note over Coord: Step 3: Order Amenities
    Coord->>Amen: Check amenities at location
    Amen->>APIs: Query Starbucks menu
    APIs-->>Amen: Menu available
    Amen->>APIs: Place order (Large Latte)
    APIs-->>Amen: Order confirmed, ready 10:20 AM
    Amen-->>Coord: Order placed: $5.50
    
    Note over Coord: Step 4: Process Payment
    Coord->>Pay: Process transactions
    Pay->>APIs: Charge wallet for food
    APIs-->>Pay: Payment successful
    Pay-->>Coord: Paid: $5.50
    
    Note over Coord: Step 5: Generate Summary
    Coord->>Coord: Compile all results
    Coord->>UI: Return complete summary
    UI->>User: Display confirmation
    
    Note over Mon: Background Monitoring
    Mon->>APIs: Check charger status (every 5 min)
    APIs-->>Mon: Status: Online
    
    alt Charger goes offline
        Mon->>APIs: Detect offline status
        Mon->>Charge: Find alternative charger
        Charge->>APIs: Search & reserve backup
        Mon->>Amen: Move food order
        Mon->>UI: Alert user of change
        UI->>User: "Rebooked at Bakersfield"
    end
```

## Agent Communication Flow

```mermaid
graph TB
    subgraph "User Layer"
        A[User Input via Chat]
    end
    
    subgraph "Coordinator Layer"
        B[Coordinator Agent]
        B1[Parse Request]
        B2[Orchestrate Agents]
        B3[Generate Summary]
        B-->B1-->B2-->B3
    end
    
    subgraph "Specialized Agents"
        C[Trip Planning Agent]
        D[Charging Negotiation Agent]
        E[Amenities Agent]
        F[Payment Agent]
        G[Monitoring Agent]
    end
    
    subgraph "Tool Layer"
        H[Route Tools]
        I[Charging Tools]
        J[Amenities Tools]
        K[Payment Tools]
    end
    
    subgraph "External Services"
        L[Google Maps API]
        M[EVgo API]
        N[ChargePoint API]
        O[Starbucks API]
        P[Stripe API]
    end
    
    A-->B1
    B2-->C
    B2-->D
    B2-->E
    B2-->F
    B2-->G
    
    C-->H-->L
    D-->I-->M
    D-->I-->N
    E-->J-->O
    F-->K-->P
    
    C-->B3
    D-->B3
    E-->B3
    F-->B3
    G-->B3
    
    B3-->A
```

## Decision Tree: Charging Strategy

```mermaid
graph TD
    A[User Request] --> B{Parse Trip Details}
    B --> C[Calculate Energy Needs]
    C --> D{Charging Needed?}
    
    D -->|No| E[✅ Sufficient Range]
    E --> F[Send Confirmation]
    
    D -->|Yes| G{Current Battery Level}
    G -->|< 30%| H[Strategy: Pre-Trip Charging]
    G -->|≥ 30%| I[Strategy: En-Route Charging]
    
    H --> J[Search Nearby Chargers]
    I --> K[Search Route Chargers]
    
    J --> L[Compare Options]
    K --> L
    
    L --> M{User Preference?}
    M -->|Speed| N[Select Fastest Charger]
    M -->|Cost| O[Select Cheapest Charger]
    M -->|Convenience| P[Select Closest Charger]
    
    N --> Q[Reserve Slot]
    O --> Q
    P --> Q
    
    Q --> R{Auto-Order Food?}
    R -->|Yes| S[Check Amenities]
    R -->|No| T[Skip Food Order]
    
    S --> U[Place Order]
    U --> V[Process Payment]
    T --> V
    
    V --> W[Generate Summary]
    W --> X[Send to User]
```

## State Machine: Reservation Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Searching: User requests trip
    Searching --> Comparing: Chargers found
    Comparing --> Reserving: Best option selected
    Reserving --> Reserved: Confirmation received
    
    Reserved --> Monitoring: Background monitoring starts
    Monitoring --> Reserved: Status OK
    Monitoring --> Rebooking: Charger offline detected
    
    Rebooking --> Searching: Find alternative
    
    Reserved --> InProgress: User arrives at charger
    InProgress --> Completed: Charging finished
    
    Completed --> [*]: Trip complete
    
    Reserved --> Cancelled: User cancels trip
    Cancelled --> [*]
```

## Data Flow: Trip to Confirmation

```mermaid
flowchart LR
    A[User Message] --> B[Parse Input]
    B --> C[Extract Trip Data]
    C --> D[Extract Vehicle Data]
    
    D --> E[Trip Planning Agent]
    E --> F[Energy Calculation]
    F --> G{Needs Charge?}
    
    G -->|Yes| H[Charging Agent]
    G -->|No| I[Confirmation Only]
    
    H --> J[Search Networks]
    J --> K[Compare Results]
    K --> L[Reserve Best]
    
    L --> M[Amenities Agent]
    M --> N[Check Location]
    N --> O[Place Order]
    
    O --> P[Payment Agent]
    P --> Q[Process Transactions]
    
    Q --> R[Coordinator]
    R --> S[Generate Summary]
    S --> T[Display to User]
    
    I --> T
```

## Tool Execution Flow

```mermaid
graph LR
    subgraph "Agent Decision"
        A[Agent receives task]
        A --> B[Analyze requirements]
        B --> C[Select tools]
    end
    
    subgraph "Tool Execution"
        C --> D[Tool 1: Search]
        C --> E[Tool 2: Compare]
        C --> F[Tool 3: Reserve]
        
        D --> G[API Call]
        E --> H[API Call]
        F --> I[API Call]
    end
    
    subgraph "Result Processing"
        G --> J[Parse Response]
        H --> J
        I --> J
        
        J --> K[Validate Data]
        K --> L[Return to Agent]
    end
    
    L --> M[Agent processes results]
    M --> N[Return to Coordinator]
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Agent Action] --> B{Success?}
    
    B -->|Yes| C[Continue Workflow]
    
    B -->|No| D{Error Type}
    
    D -->|API Timeout| E[Retry with Backoff]
    E --> F{Retry Success?}
    F -->|Yes| C
    F -->|No| G[Use Fallback]
    
    D -->|Charger Offline| H[Find Alternative]
    H --> I[Rebook Automatically]
    I --> J[Notify User]
    J --> C
    
    D -->|Payment Failed| K[Alert User]
    K --> L[Request Manual Payment]
    
    D -->|Unknown Error| M[Log Error]
    M --> N[Graceful Degradation]
    N --> O[Partial Success Response]
    
    G --> C
    L --> C
    O --> C
```

## Real-Time Monitoring Loop

```mermaid
sequenceDiagram
    participant Mon as Monitoring Agent
    participant API as Charger API
    participant Coord as Coordinator
    participant User
    
    loop Every 5 minutes
        Mon->>API: Check charger status
        API-->>Mon: Status response
        
        alt Status: Online
            Mon->>Mon: Continue monitoring
        else Status: Offline
            Mon->>Coord: Alert: Charger offline
            Coord->>Coord: Trigger rebooking workflow
            Coord->>User: Send notification
            User-->>Coord: Acknowledge
        else Status: Busy
            Mon->>Coord: Alert: Longer wait expected
            Coord->>User: Update ETA
        end
    end
```

## Multi-Agent Parallel Execution

```mermaid
gantt
    title Agent Execution Timeline
    dateFormat  ss
    axisFormat %S
    
    section Coordinator
    Parse Request           :00, 2s
    Orchestrate            :02, 1s
    Generate Summary       :18, 2s
    
    section Trip Planning
    Analyze Energy         :03, 3s
    
    section Charging
    Search Networks        :06, 4s
    Reserve Slot          :10, 2s
    
    section Amenities
    Check Location        :12, 2s
    Place Order           :14, 2s
    
    section Payment
    Process Payment       :16, 2s
```

## Summary

This workflow demonstrates:
- **Sequential coordination** for dependent tasks
- **Parallel execution** where possible (amenities + payment)
- **Error handling** with automatic recovery
- **Real-time monitoring** for proactive issue resolution
- **Clear communication** between all agents

The entire workflow typically completes in **under 30 seconds** from user request to confirmation.
