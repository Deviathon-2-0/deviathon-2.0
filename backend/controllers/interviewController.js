/**
 * IMAIRA+ Interview Controller
 * Handles business logic for mock interviews, domains, and calibration metrics.
 */

// Simulated technical domains based on IMAIRA+ curriculum
const domains = [
  {
    id: "domain-01",
    code: "DOMAIN 01",
    level: "STAFF / PRINCIPAL",
    title: "Distributed Systems Architecture",
    description: "Consensus protocols, Raft/Paxos invariants, fault tolerance under network partitions, and strong replication guarantees.",
    prompt: "Design a zero-data-loss cross-region replication layer under degraded transit."
  },
  {
    id: "domain-02",
    code: "DOMAIN 02",
    level: "INFRA CORE",
    title: "Storage Engines & Databases",
    description: "LSM-Trees vs B-Trees, Write-Ahead Logging (WAL), MVCC concurrency control, and storage compaction trade-offs.",
    prompt: "Explain write amplification trade-offs between leveled and size-tiered compaction."
  },
  {
    id: "domain-03",
    code: "DOMAIN 03",
    level: "LARGE SCALE AI",
    title: "ML Infrastructure & Sharding",
    description: "Tensor and pipeline parallelism, NCCL ring all-reduce communication collectives, and high-bandwidth interconnects.",
    prompt: "Size an inter-node 3D parallelism topology for a 405B parameter model under InfiniBand."
  }
];

// Return list of available domains
exports.getDomains = (req, res) => {
  res.status(200).json({
    success: true,
    count: domains.length,
    data: domains
  });
};

// Start a new mock interview session
exports.startSession = (req, res) => {
  const { domainId, candidateName } = req.body;

  const selectedDomain = domains.find(d => d.id === domainId) || domains[0];

  const session = {
    sessionId: "sess_" + Math.random().toString(36).substring(2, 11),
    candidateName: candidateName || "Anonymous Candidate",
    coach: "Rory",
    status: "active",
    domain: selectedDomain,
    startedAt: new Date().toISOString(),
    telemetry: {
      neutralityDrift: "0.00%",
      speechToLogicLatency: "12ms",
      activeLayer: "Layer 01: Acoustic Normalization"
    }
  };

  res.status(201).json({
    success: true,
    message: "Mock interview session initiated with Rory",
    data: session
  });
};

// Retrieve benchmark fairness telemetry
exports.getFairnessMetrics = (req, res) => {
  res.status(200).json({
    success: true,
    data: {
      testedCandidates: 12400,
      continentalHubs: 5,
      acousticDelta: "< 0.04%",
      statisticalDrift: "0.00%",
      regionalAverages: [
        { region: "Indian Subcontinent (Hindi / Tamil / Bengali)", scoreDelta: "+0.03%", status: "Neutral" },
        { region: "East Asia (Mandarin / Japanese / Korean)", scoreDelta: "+0.04%", status: "Neutral" },
        { region: "Eastern Europe & Latin America", scoreDelta: "+0.02%", status: "Neutral" }
      ]
    }
  });
};
