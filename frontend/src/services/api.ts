import axios from 'axios';
import { ChatResponse, NetworkStatus, Ticket } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock database to persist local states (like tickets or network incidents)
export const MOCK_TICKETS: Ticket[] = [
  {
    ticket_id: "TKT-B82F10A4",
    category: "billing",
    severity: "high",
    status: "open",
    summary: "Customer charged Rs. 12,000 for roaming unfairly on a 2-day domestic trip.",
    customer_mobile: "9876543210",
    preferred_contact: "call",
    eta_hours: 8,
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    reference_url: "https://support.telecom.com/tickets/TKT-B82F10A4"
  },
  {
    ticket_id: "TKT-A49E82D5",
    category: "network",
    severity: "critical",
    status: "in_progress",
    summary: "Major 4G outage reported in Mumbai region due to optical fiber cut.",
    customer_mobile: "9911223344",
    preferred_contact: "sms",
    eta_hours: 2,
    created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
    reference_url: "https://support.telecom.com/tickets/TKT-A49E82D5"
  },
  {
    ticket_id: "TKT-C73D1902",
    category: "account",
    severity: "medium",
    status: "closed",
    summary: "SIM card swapping request verification failure for Aadhar OTP.",
    customer_mobile: "9000110022",
    preferred_contact: "call",
    eta_hours: 24,
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    reference_url: "https://support.telecom.com/tickets/TKT-C73D1902"
  }
];

export const MOCK_NETWORK_STATUS: NetworkStatus[] = [
  {
    region: "Mumbai",
    status: "outage",
    active_incident: true,
    incident_id: "INC-4821",
    incident_summary: "Partial 4G data outage in Mumbai due to optical fiber cut. ETA 4:00 PM.",
    affected_services: ["4G Data", "Voice Calls"],
    estimated_resolution: new Date(Date.now() + 3600000 * 3).toISOString()
  },
  {
    region: "Delhi",
    status: "healthy",
    active_incident: false,
    affected_services: []
  },
  {
    region: "Bangalore",
    status: "degraded",
    active_incident: true,
    incident_id: "MAINT-112",
    incident_summary: "Planned maintenance work in Bangalore central grid. 4G/5G may fail intermittently.",
    affected_services: ["5G Data", "SMS Services"],
    estimated_resolution: new Date(Date.now() + 3600000 * 5).toISOString()
  },
  {
    region: "Ahmedabad",
    status: "healthy",
    active_incident: false,
    affected_services: []
  },
  {
    region: "Chennai",
    status: "healthy",
    active_incident: false,
    affected_services: []
  }
];

// Helper to simulate network latency
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function sendChatMessage(query: string, history: any[]): Promise<ChatResponse> {
  try {
    const response = await apiClient.post<ChatResponse>('/chat', { query, history });
    return response.data;
  } catch (error) {
    console.warn("Backend /chat endpoint is unavailable. Falling back to intelligent mock simulation.");
    await sleep(800 + Math.random() * 600); // Realistic retrieval latency

    const lowerQuery = query.toLowerCase();

    // 1. Simulating Billing Out-of-Scope / Escalation Flow
    if (lowerQuery.includes('charge') || lowerQuery.includes('bill') || lowerQuery.includes('roaming') || lowerQuery.includes('money') || lowerQuery.includes('dispute') || lowerQuery.includes('rs.')) {
      const ticketId = `TKT-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
      const isRoaming = lowerQuery.includes('roaming');
      const amountMatch = lowerQuery.match(/(?:rs\.?\s*)(\d+)/i);
      const isHighValue = amountMatch ? parseInt(amountMatch[1]) > 5000 : false;
      const mustEscalate = isHighValue || lowerQuery.includes('roaming') || lowerQuery.includes('dispute');

      const text = isRoaming 
        ? "Postpaid international roaming plans activate automatically once the customer connects to a foreign partner network. Standard charges of Rs. 10/MB apply unless a specific custom roaming pack is pre-selected. Billing disputes can be initiated in 60 days of the invoice date."
        : "Standard billing cycles are monthly. If you spot a discrepancy in local charges or plan activations, you may file a formal billing dispute within 60 days. Form charges > Rs. 5,000 are auto-escalated to human review queues.";

      const docId = isRoaming ? "airtel_roaming_004" : "jio_billing_002";
      const sectionId = isRoaming ? "roaming_billing_pack_s2" : "billing_cycle_disputes_s1";

      const ticket: Ticket = {
        ticket_id: ticketId,
        category: "billing",
        severity: isHighValue ? "high" : "medium",
        status: "open",
        summary: `Billing escalation: ${query}`,
        customer_mobile: "9876543210",
        preferred_contact: "call",
        eta_hours: isHighValue ? 8 : 24,
        created_at: new Date().toISOString()
      };
      
      MOCK_TICKETS.unshift(ticket); // Save locally

      return {
        answer: mustEscalate 
          ? `I have identified a billing discrepancy in your query. Under Section 4.2 of the billing code, billing disputes must be investigated within 15 working days [SOURCE: ${docId}, ${sectionId}]. Your request has been escalated and ticket ${ticketId} has been created. A customer advocate will reach out to you within 8-24 hours.`
          : `You can view your detailed bill breakdown in the carrier app under Bill details. To contest any incorrect package activations, file a billing dispute within 60 days [SOURCE: ${docId}, ${sectionId}].`,
        citations: [
          { doc_id: docId, section_id: sectionId, text }
        ],
        tool_trace: [
          { tool: "SearchKB", params: { query, category_filter: "billing" }, output_summary: "1 passage retrieved: top=billing_disputes" },
          ...(mustEscalate ? [{ tool: "CreateTicket", params: { summary: query, category: "billing", severity: isHighValue ? "high" : "medium" }, output_summary: `Created ticket ${ticketId} in billing queue` }] : [])
        ],
        confidence: mustEscalate ? 0.94 : 0.88,
        escalated: mustEscalate,
        ticket_id: mustEscalate ? ticketId : null,
        retrieved: [
          {
            doc_id: docId,
            section_id: sectionId,
            heading: isRoaming ? "International Roaming Tariffs" : "Raising Bill Complaints",
            text,
            dense_score: 0.9124
          }
        ],
        latency_ms: 120 + Math.random() * 50
      };
    }

    // 2. Simulating Network Status Outage Flow
    if (lowerQuery.includes('network') || lowerQuery.includes('signal') || lowerQuery.includes('outage') || lowerQuery.includes('internet') || lowerQuery.includes('data') || lowerQuery.includes('mumbai') || lowerQuery.includes('delhi')) {
      const isMumbai = lowerQuery.includes('mumbai');
      const isBangalore = lowerQuery.includes('bangalore') || lowerQuery.includes('bengaluru');
      const region = isMumbai ? "Mumbai" : isBangalore ? "Bangalore" : "Unknown";
      
      const activeOutage = isMumbai || isBangalore;
      
      let answer = "";
      if (isMumbai) {
        answer = "I have detected an active incident in your region. A major 4G/Voice outage is ongoing in Mumbai due to a core fiber cut. Restorations are underway with an ETA of 4 hours [SOURCE: network_status_live, outage_INC-4821].";
      } else if (isBangalore) {
        answer = "We are currently conducting scheduled grid upgrades in Bangalore. Users may experience temporary degradation of 5G data speeds [SOURCE: network_status_live, maint_MAINT-112].";
      } else {
        answer = "Local network statuses are operational. If you are experiencing poor signal, please verify if your SIM is set to LTE/5G auto and toggle Flight Mode to re-register on the local cell tower [SOURCE: trai_quality_service, qos_network_signal].";
      }

      return {
        answer,
        citations: activeOutage ? [
          {
            doc_id: "network_status_live",
            section_id: isMumbai ? "outage_INC-4821" : "maint_MAINT-112",
            text: isMumbai 
              ? "ACTIVE partial outage in Mumbai. Impact: 4G data services degraded. Incident ID: INC-4821. Started: 08:00 AM. ETA: 4 hours. Compensation: Eligible."
              : "ACTIVE planned maintenance in Bangalore. Impact: 5G services intermittent. Ref ID: MAINT-112. Duration: 2-5 AM."
          }
        ] : [
          {
            doc_id: "trai_quality_service",
            section_id: "qos_network_signal",
            text: "Telecom service providers must maintain network availability > 98% in each telecom circle. In case of outages > 24 hours, users are entitled to standard pro-rata bill rebates."
          }
        ],
        tool_trace: [
          { tool: "SearchKB", params: { query, category_filter: "network" }, output_summary: "2 passages retrieved: top=qos_network_signal" },
          { tool: "CheckNetworkStatus", params: { region, service_type: "all" }, output_summary: `Region=${region} status=${isMumbai ? 'outage' : isBangalore ? 'degraded' : 'operational'}` }
        ],
        confidence: 0.97,
        escalated: false,
        ticket_id: null,
        retrieved: [
          {
            doc_id: activeOutage ? "network_status_live" : "trai_quality_service",
            section_id: activeOutage ? (isMumbai ? "outage_INC-4821" : "maint_MAINT-112") : "qos_network_signal",
            heading: activeOutage ? `Network Outage Bulletin - ${region}` : "TRAI Quality of Service (QoS) Regulations",
            text: activeOutage 
              ? `Real-time outage registered in the ${region} grid. Services affected: ${isMumbai ? '4G Data, Voice' : '5G Data'}.`
              : "Quality standards require service providers to resolve local tower disruptions in 48 hours.",
            dense_score: 0.9542
          }
        ],
        latency_ms: 180 + Math.random() * 40
      };
    }

    // 3. Simulating Policy Lookup
    if (lowerQuery.includes('policy') || lowerQuery.includes('rule') || lowerQuery.includes('complaint') || lowerQuery.includes('trai')) {
      return {
        answer: "Under TRAI consumer charter, customers have the right to port their mobile connection (Mobile Number Portability / MNP) to any other service provider after 90 days of activation. UPCH (Unique Porting Code) must be generated by sending 'PORT <mobile>' to 1900 [SOURCE: trai_consumer_charter, mnp_section_2].",
        citations: [
          {
            doc_id: "trai_consumer_charter",
            section_id: "mnp_section_2",
            text: "Consumers can request mobile number portability (MNP) to any other telecom service provider in their service area. The current service provider must release the number in 3 working days if there are no outstanding postpaid balances."
          }
        ],
        tool_trace: [
          { tool: "SearchKB", params: { query, category_filter: "any" }, output_summary: "1 passage retrieved: top=mnp_section_2" },
          { tool: "GetPolicy", params: { section_id: "mnp_section_2" }, output_summary: "Fetched full text for MNP section 2" }
        ],
        confidence: 0.91,
        escalated: false,
        ticket_id: null,
        retrieved: [
          {
            doc_id: "trai_consumer_charter",
            section_id: "mnp_section_2",
            heading: "Mobile Number Portability Eligibility",
            text: "Consumers can request mobile number portability (MNP) to any other telecom service provider in their service area.",
            dense_score: 0.8931
          }
        ],
        latency_ms: 140 + Math.random() * 20
      };
    }

    // 4. Default generic response
    return {
      answer: "To manage your active mobile plan, change your account credentials, or request service swaps, please use the self-service portal or dial 198. For eSIM profiles, scan the barcode mailed to your registered email [SOURCE: telecom_general_faq, esim_activation_s1].",
      citations: [
        {
          doc_id: "telecom_general_faq",
          section_id: "esim_activation_s1",
          text: "eSIM activation requires generating an eSIM request in the app. The QR profile is generated and sent to the customer's registered email in 2 hours."
        }
      ],
      tool_trace: [
        { tool: "SearchKB", params: { query, category_filter: "any" }, output_summary: "1 passage retrieved: top=esim_activation_s1" }
      ],
      confidence: 0.76,
      escalated: false,
      ticket_id: null,
      retrieved: [
        {
          doc_id: "telecom_general_faq",
          section_id: "esim_activation_s1",
          heading: "Active eSIM Swaps",
          text: "eSIM activation requires generating an eSIM request in the app.",
          dense_score: 0.7812
        }
      ],
      latency_ms: 220 + Math.random() * 30
    };
  }
}

export async function getNetworkStatus(): Promise<NetworkStatus[]> {
  await sleep(400); // Simulate API latency
  return [...MOCK_NETWORK_STATUS];
}

export async function getTickets(): Promise<Ticket[]> {
  await sleep(350); // Simulate API latency
  return [...MOCK_TICKETS];
}
