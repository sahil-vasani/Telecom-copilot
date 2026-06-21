export interface Citation {
  doc_id: string;
  section_id: string;
  text?: string; // Optional full text lookup
}

export interface ToolTrace {
  tool: string;
  params: Record<string, any>;
  output_summary: string;
}

export interface RetrievedDocument {
  doc_id: string;
  section_id: string;
  heading: string;
  text: string;
  dense_score: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  tool_trace: ToolTrace[];
  confidence: number;
  escalated: boolean;
  ticket_id: string | null;
  retrieved: RetrievedDocument[];
  latency_ms: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  // Metadata for assistant responses
  citations?: Citation[];
  toolTrace?: ToolTrace[];
  confidence?: number;
  escalated?: boolean;
  ticketId?: string | null;
  retrieved?: RetrievedDocument[];
  latencyMs?: number;
  isLoading?: boolean;
  error?: string;
}

export interface NetworkStatus {
  region: string;
  status: 'healthy' | 'degraded' | 'outage';
  active_incident: boolean;
  incident_id?: string | null;
  incident_summary?: string | null;
  affected_services: string[];
  estimated_resolution?: string | null;
}

export interface Ticket {
  ticket_id: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'closed';
  summary: string;
  customer_mobile?: string;
  preferred_contact?: string;
  eta_hours: number;
  created_at: string;
  reference_url?: string;
}

export interface SystemMetrics {
  citationRecall: number;
  escalationAccuracy: number;
  outageAwareRate: number;
  rougeL: number;
  bertScore: number;
  avgLatency: number;
  p95Latency: number;
}
