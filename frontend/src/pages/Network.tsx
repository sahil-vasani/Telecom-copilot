import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getNetworkStatus } from '../services/api';
import { NetworkStatus } from '../types';
import { Activity, ShieldAlert, CheckCircle, Wifi, AlertTriangle, AlertCircle, RefreshCw } from 'lucide-react';

const Network: React.FC = () => {
  const [regions, setRegions] = useState<NetworkStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const data = await getNetworkStatus();
        setRegions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [refreshKey]);

  const getStatusConfig = (status: NetworkStatus['status']) => {
    switch (status) {
      case 'healthy':
        return {
          color: 'text-success border-success/20 bg-success/5',
          dot: 'bg-success',
          bg: 'bg-success/10',
          pulse: 'bg-success/40',
          label: 'Operational'
        };
      case 'degraded':
        return {
          color: 'text-warning border-warning/20 bg-warning/5',
          dot: 'bg-warning',
          bg: 'bg-warning/10',
          pulse: 'bg-warning/40',
          label: 'Degraded'
        };
      case 'outage':
        return {
          color: 'text-error border-error/20 bg-error/5',
          dot: 'bg-error',
          bg: 'bg-error/10',
          pulse: 'bg-error/40',
          label: 'Active Incident'
        };
    }
  };

  const getOverallStatus = () => {
    const outages = regions.filter(r => r.status === 'outage').length;
    const degraded = regions.filter(r => r.status === 'degraded').length;
    if (outages > 0) return { label: `${outages} Critical Outages`, icon: AlertCircle, color: 'text-error' };
    if (degraded > 0) return { label: `${degraded} Service Upgrades`, icon: AlertTriangle, color: 'text-warning' };
    return { label: "All Networks Operational", icon: CheckCircle, color: 'text-success' };
  };

  const overall = getOverallStatus();
  const OverallIcon = overall.icon;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-textPrimary text-left">Network Status Center</h1>
          <p className="text-xs text-textSecondary mt-0.5 text-left">Live operations telemetries across regional network grids.</p>
        </div>
        <button 
          onClick={() => setRefreshKey(prev => prev + 1)}
          className="self-start flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-borderDark hover:bg-white/5 text-xs font-semibold rounded-lg transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Force Refresh</span>
        </button>
      </div>

      {/* Aggregate Overview Card */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary/10 rounded-xl border border-primary/20 shrink-0">
            <Wifi className="h-6 w-6 text-primary animate-pulse-slow" />
          </div>
          <div className="text-left">
            <span className="text-[10px] text-textSecondary uppercase tracking-widest font-mono">System Health</span>
            <div className="flex items-center gap-2 mt-1">
              <OverallIcon className={`h-5 w-5 ${overall.color}`} />
              <p className="text-lg font-bold text-textPrimary leading-none">{overall.label}</p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 text-xs font-mono">
          <div className="bg-slate-950/40 px-4 py-2.5 rounded-xl border border-borderDark text-left">
            <p className="text-[9px] text-textSecondary">Average QoS</p>
            <p className="font-semibold text-textPrimary mt-0.5">99.84%</p>
          </div>
          <div className="bg-slate-950/40 px-4 py-2.5 rounded-xl border border-borderDark text-left">
            <p className="text-[9px] text-textSecondary">Global Incident Rate</p>
            <p className="font-semibold text-textPrimary mt-0.5">0.02/hr</p>
          </div>
          <div className="bg-slate-950/40 px-4 py-2.5 rounded-xl border border-borderDark text-left">
            <p className="text-[9px] text-textSecondary">Active Grids</p>
            <p className="font-semibold text-textPrimary mt-0.5">{regions.length}/5</p>
          </div>
        </div>
      </div>

      {/* Grids list */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="glass-panel h-52 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {regions.map((region) => {
            const config = getStatusConfig(region.status);
            return (
              <motion.div
                key={region.region}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
                className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-52 relative overflow-hidden group hover:border-slate-800"
              >
                {/* Background aura gradient on hover */}
                <div className={`absolute -right-16 -top-16 h-32 w-32 rounded-full blur-3xl opacity-10 group-hover:opacity-20 transition-opacity ${config.bg}`} />

                {/* Card Top */}
                <div className="flex items-start justify-between gap-4">
                  <div className="text-left">
                    <h3 className="text-base font-bold text-textPrimary leading-none">{region.region}</h3>
                    <span className="text-[10px] text-textSecondary font-semibold uppercase tracking-wider mt-1 block">Grid Circle</span>
                  </div>
                  {/* Status badge */}
                  <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold ${config.color}`}>
                    <div className="relative flex h-2 w-2">
                      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${config.pulse}`} />
                      <span className={`relative inline-flex rounded-full h-2 w-2 ${config.dot}`} />
                    </div>
                    <span>{config.label}</span>
                  </div>
                </div>

                {/* Incident details (if active) */}
                <div className="my-3 text-left">
                  {region.active_incident ? (
                    <div className="space-y-1">
                      <p className="text-[10px] font-mono text-textSecondary uppercase tracking-wider font-semibold">Incident detail</p>
                      <p className="text-xs text-textPrimary leading-tight truncate">{region.incident_summary}</p>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-xs text-success bg-success/5 border border-success/10 py-1.5 px-3 rounded-lg w-fit">
                      <CheckCircle className="h-3.5 w-3.5" />
                      <span>All carrier towers operational.</span>
                    </div>
                  )}
                </div>

                {/* Card Bottom */}
                <div className="flex items-center justify-between border-t border-white/5 pt-3 text-xs font-mono text-textSecondary">
                  <div>
                    <span className="text-[9px] block">ETA Resolution</span>
                    <span className="text-textPrimary font-medium mt-0.5 block">
                      {region.estimated_resolution 
                        ? new Date(region.estimated_resolution).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : 'N/A'}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="text-[9px] block">Affected Services</span>
                    <span className="text-textPrimary font-medium mt-0.5 block truncate max-w-[120px]">
                      {region.affected_services.length > 0 ? region.affected_services.join(', ') : 'None'}
                    </span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Incidents logs timeline */}
      <div className="glass-panel p-6 rounded-2xl text-left">
        <h2 className="text-sm font-bold text-textPrimary uppercase tracking-wider mb-4 flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-primary" />
          <span>Active Incident Logs</span>
        </h2>
        <div className="space-y-3 font-mono text-xs text-textSecondary">
          {regions.filter(r => r.active_incident).map((region, i) => (
            <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 bg-slate-950/30 rounded-xl border border-borderDark">
              <div className="flex items-start sm:items-center gap-2">
                <span className="px-2 py-0.5 text-[10px] bg-error/10 border border-error/20 text-error rounded font-bold uppercase">
                  {region.incident_id || 'MAINT'}
                </span>
                <p className="text-textPrimary leading-none">{region.incident_summary}</p>
              </div>
              <span className="text-[10px] text-textSecondary/80">Region: {region.region}</span>
            </div>
          ))}
          {regions.filter(r => r.active_incident).length === 0 && (
            <p className="text-center py-4 text-xs text-textSecondary">No critical network incidents recorded.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Network;
