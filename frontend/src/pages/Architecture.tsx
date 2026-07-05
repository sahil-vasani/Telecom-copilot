import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Bot, Cpu, Database, Network, Search, Award } from 'lucide-react';
import { cn } from '../utils/helpers';

interface ArchNode {
  id: string;
  name: string;
  icon: any;
  modelType: string;
  description: string;
  input: string;
  output: string;
  details: string[];
}

const NODES: ArchNode[] = [
  {
    id: 'query',
    name: 'User Query',
    icon: Bot,
    modelType: 'User Interface',
    description: 'Incoming customer request or query regarding plans, billing, networks, or account issues.',
    input: 'Plain text natural language complaint',
    output: 'Query string + session history',
    details: [
      'Captures user intent and categorizes language patterns',
      'Stores prior chat history turns for session memory tracking',
      'Provides triggers for suggested queries and operations'
    ]
  },
  {
    id: 'router',
    name: 'Tool Router Classifier',
    icon: Cpu,
    modelType: 'Fine-Tuned BERT Base (Sequence Classifier)',
    description: 'Classifies the query intent to route it to one or more appropriate backend tools.',
    input: 'Query text + history state',
    output: 'List of target tool calls with parameters',
    details: [
      'Fine-tuned on labeled telecom intents',
      'High accuracy intent classification (92.2% GEA)',
      'Falls back to rule-based keyword router if model is offline'
    ]
  },
  {
    id: 'retriever',
    name: 'Dense Retriever',
    icon: Search,
    modelType: 'Fine-Tuned BGE Large v1.5 (Embedding + FAISS)',
    description: 'Embeds queries and searches a pre-built vector index for the top-20 most similar documents.',
    input: 'Natural language search query',
    output: 'Top-20 retrieved passage objects',
    details: [
      'BAAI/bge-large-en-v1.5 base model fine-tuned using MNRL',
      'Retrieves context using cosine similarity over exact IndexFlatIP index',
      'Contains 25,000+ indexed carrier FAQ paragraphs'
    ]
  },
  {
    id: 'reranker',
    name: 'Cross-Encoder Reranker',
    icon: Database,
    modelType: 'Fine-Tuned MiniLM Cross-Encoder',
    description: 'Performs query-passage cross-attention to score and select the top-3 most relevant snippets.',
    input: 'Query + Top-20 dense candidates list',
    output: 'Top-3 re-scored passages',
    details: [
      'Fine-tuned on MultiDoc2Dial retrieval triples',
      'Computes full token-level query-context interactions',
      'Improves retrieval precision while reducing context window length'
    ]
  },
  {
    id: 'tools',
    name: 'Tool Execution Layer',
    icon: Network,
    modelType: 'Modular Tool dispatcher',
    description: 'Wired execution logic connecting API grids, span lookups, and ticket logging database.',
    input: 'Tool parameter definitions',
    output: 'Live status records, ticket IDs, policy texts',
    details: [
      'CheckNetworkStatus: Simulates live operational tower checks',
      'GetPolicy: Performs exact span-level lookups in span_index.json',
      'CreateTicket: Persists formal complaint tickets to data store'
    ]
  },
  {
    id: 'generator',
    name: 'Grounded Generator',
    icon: Award,
    modelType: 'DoRA Fine-Tuned Flan-T5-base / OpenRouter API',
    description: 'Drafts the final response by strictly grounding the answer in the retrieved facts and formatting citations.',
    input: 'Top-3 Reranked contexts + Tool outputs + Query',
    output: 'Structured grounded response + citation nodes',
    details: [
      'Fine-tuned using Weight-Decomposed Low-Rank Adaptation (DoRA)',
      'Adheres to strict prompts to prevent hallucinations',
      'Formats source tracking tags like [SOURCE: doc_id, section_id]'
    ]
  }
];

const Architecture: React.FC = () => {
  const [activeNode, setActiveNode] = useState<ArchNode>(NODES[0]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-left">
        <h1 className="text-xl font-bold text-textPrimary leading-none">System Architecture</h1>
        <p className="text-xs text-textSecondary mt-0.5">Explore the end-to-end logical flow of the TelecomRAG Agentic Copilot.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 items-start">
        {/* LEFT PIPELINE VISUALIZATION (60%) */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-2xl">
          <h2 className="text-xs font-bold text-textSecondary uppercase tracking-widest mb-6 text-left">
            Interactive Control Flow
          </h2>

          <div className="flex flex-col items-center space-y-4">
            {NODES.map((node, index) => {
              const NodeIcon = node.icon;
              const isSelected = activeNode.id === node.id;
              
              return (
                <React.Fragment key={node.id}>
                  {/* Node Button */}
                  <motion.button
                    onClick={() => setActiveNode(node)}
                    whileHover={{ scale: 1.01 }}
                    className={cn(
                      "w-full max-w-md flex items-center gap-4 p-4 rounded-xl border transition-all text-left",
                      isSelected
                        ? "bg-primary/10 border-primary text-textPrimary shadow-[0_0_15px_rgba(0,229,255,0.15)]"
                        : "bg-slate-900/40 border-borderDark hover:border-slate-700 text-textSecondary"
                    )}
                  >
                    <div className={cn(
                      "p-2.5 rounded-lg border shrink-0",
                      isSelected ? "bg-primary/10 border-primary/20 text-primary animate-pulse" : "bg-slate-950/40 border-borderDark text-textSecondary"
                    )}>
                      <NodeIcon className="h-5 w-5" />
                    </div>
                    <div className="truncate">
                      <h3 className="text-xs font-bold text-textPrimary leading-none">{node.name}</h3>
                      <span className="text-[9px] font-mono text-textSecondary mt-1 block truncate">
                        {node.modelType}
                      </span>
                    </div>
                  </motion.button>

                  {/* Connecting Arrow */}
                  {index < NODES.length - 1 && (
                    <motion.div 
                      animate={isSelected ? { y: [0, 4, 0] } : {}}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                      className="flex items-center justify-center py-1"
                    >
                      <ArrowRight className="h-4 w-4 text-textSecondary/50 rotate-90" />
                    </motion.div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* RIGHT DETAIL INSPECTOR PANEL (40%) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl text-left space-y-5">
            {/* Header details */}
            <div className="border-b border-borderDark pb-4">
              <span className="text-[9px] font-mono font-bold text-primary uppercase tracking-widest bg-primary/10 px-2 py-1 rounded border border-primary/20">
                Pipeline Inspector
              </span>
              <h2 className="text-lg font-bold text-textPrimary mt-3 leading-none">{activeNode.name}</h2>
              <p className="text-[10px] font-mono text-textSecondary mt-1.5">{activeNode.modelType}</p>
            </div>

            {/* Description */}
            <div className="space-y-1">
              <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-wider">Functional Role</h4>
              <p className="text-xs text-textPrimary leading-normal">{activeNode.description}</p>
            </div>

            {/* In / Out definitions */}
            <div className="grid grid-cols-2 gap-4 text-[10px] font-mono">
              <div className="bg-slate-950/45 p-3 rounded-xl border border-borderDark">
                <span className="text-textSecondary block">Input Data</span>
                <span className="text-textPrimary font-semibold mt-1 block leading-tight">{activeNode.input}</span>
              </div>
              <div className="bg-slate-950/45 p-3 rounded-xl border border-borderDark">
                <span className="text-textSecondary block">Output Data</span>
                <span className="text-textPrimary font-semibold mt-1 block leading-tight">{activeNode.output}</span>
              </div>
            </div>

            {/* Detailed list bullets */}
            <div className="space-y-2">
              <h4 className="text-[10px] font-bold text-textSecondary uppercase tracking-wider">Operational Notes</h4>
              <ul className="space-y-1.5 text-xs text-textSecondary">
                {activeNode.details.map((detail, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="h-1.5 w-1.5 bg-primary rounded-full mt-1.5 shrink-0" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Architecture;
