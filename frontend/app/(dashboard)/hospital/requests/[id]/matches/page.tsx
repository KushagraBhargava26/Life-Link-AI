'use client';

// frontend/app/(dashboard)/hospital/requests/[id]/matches/page.tsx
// LifeLink AI — Hospital Matching & Coordination Workspace (Phase 1.6)
// Architecture Reference: ARCHITECTURE.md ADR-004 & Section 17

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { emergencyService } from '@/services/emergencyService';
import { matchingService } from '@/services/matchingService';
import { EmergencyRequestData, MatchRun, MatchCandidate, MatchCandidateStatus } from '@/types';

export default function HospitalMatchingWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const requestId = params?.id as string;

  const [request, setRequest] = useState<EmergencyRequestData | null>(null);
  const [matchRun, setMatchRun] = useState<MatchRun | null>(null);
  const [searchRadius, setSearchRadius] = useState<number>(50.0);
  const [isLoadingRequest, setIsLoadingRequest] = useState<boolean>(true);
  const [isMatchingRunning, setIsMatchingRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchRequestDetails = useCallback(async () => {
    if (!requestId) return;
    try {
      setIsLoadingRequest(true);
      const res = await emergencyService.getRequest(requestId);
      if (res.success && res.data) {
        setRequest(res.data);
      } else {
        setError('Could not find the emergency requisition details.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to load requisition.');
    } finally {
      setIsLoadingRequest(false);
    }
  }, [requestId]);

  const fetchMatches = useCallback(async (radius: number = 50.0) => {
    if (!requestId) return;
    try {
      setIsMatchingRunning(true);
      setError(null);
      const res = await matchingService.getMatches(requestId);
      if (res.success && res.data) {
        setMatchRun(res.data);
        setSearchRadius(res.data.search_radius_km || radius);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to execute matching.');
    } finally {
      setIsMatchingRunning(false);
    }
  }, [requestId]);

  const handleReRunMatching = async (radius: number) => {
    if (!requestId) return;
    try {
      setIsMatchingRunning(true);
      setError(null);
      setActionMessage(null);
      setSearchRadius(radius);
      const res = await matchingService.runMatching(requestId, radius);
      if (res.success && res.data) {
        setMatchRun(res.data);
        setActionMessage(`Matching algorithm executed (${res.data.blood_banks_matched} blood banks, ${res.data.donors_matched} donors found).`);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to re-run matching.');
    } finally {
      setIsMatchingRunning(false);
    }
  };

  const handleCandidateStatusUpdate = async (candidateId: string, newStatus: MatchCandidateStatus) => {
    if (!requestId) return;
    try {
      const res = await matchingService.updateCandidateStatus(requestId, candidateId, newStatus);
      if (res.success) {
        setActionMessage(`Candidate marked as ${newStatus}.`);
        // Update candidate in local state
        setMatchRun((prev) => {
          if (!prev) return prev;
          const updatedBB = prev.blood_banks.map((c) =>
            c.id === candidateId ? { ...c, status: newStatus } : c
          );
          const updatedDonors = prev.donors.map((c) =>
            c.id === candidateId ? { ...c, status: newStatus } : c
          );
          return { ...prev, blood_banks: updatedBB, donors: updatedDonors };
        });
      }
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to update candidate status.');
    }
  };

  useEffect(() => {
    fetchRequestDetails();
    fetchMatches(searchRadius);
  }, [fetchRequestDetails, fetchMatches, searchRadius]);

  if (isLoadingRequest) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-text-muted text-sm font-medium">Loading emergency requisition...</p>
      </div>
    );
  }

  const bloodBanks = matchRun?.blood_banks || [];
  const donors = matchRun?.donors || [];
  const totalCandidates = bloodBanks.length + donors.length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Top Breadcrumb & Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <Link href="/hospital" className="hover:text-primary transition-colors">
            Hospital Portal
          </Link>
          <span>/</span>
          <Link href="/hospital/requests" className="hover:text-primary transition-colors">
            Emergency Requests
          </Link>
          <span>/</span>
          <span className="text-text font-semibold">{request?.request_number || 'Requisition'}</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href={`/emergency/track/${request?.request_number || request?.id}`}>
            <Button variant="outline" size="sm">
              Public Tracking View ↗
            </Button>
          </Link>
          <Link href="/hospital/requests">
            <Button variant="secondary" size="sm">
              ← Back to Requisitions
            </Button>
          </Link>
        </div>
      </div>

      {/* Action / Error Banners */}
      {error && (
        <div className="p-4 bg-critical/10 border border-critical/30 rounded-xl text-critical text-sm flex items-center justify-between">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)} className="font-bold text-lg leading-none">×</button>
        </div>
      )}
      {actionMessage && (
        <div className="p-4 bg-success/10 border border-success/30 rounded-xl text-success text-sm flex items-center justify-between">
          <span>✓ {actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="font-bold text-lg leading-none">×</button>
        </div>
      )}

      {/* Requisition Overview Banner */}
      <Card className="border-border bg-card">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-2xl font-black font-mono text-primary bg-primary/10 px-3 py-1 rounded-lg border border-primary/20">
                  {request?.blood_type}
                </span>
                <h1 className="text-xl sm:text-2xl font-bold text-text">
                  Requisition {request?.request_number}
                </h1>
                <Badge
                  variant={
                    request?.urgency_level === 'CRITICAL'
                      ? 'critical'
                      : request?.urgency_level === 'HIGH'
                      ? 'high'
                      : 'medium'
                  }
                  size="md"
                >
                  {request?.urgency_level} URGENCY
                </Badge>
                <Badge variant="outline" size="md">
                  Status: {request?.status}
                </Badge>
              </div>
              <p className="text-sm text-text-muted">
                Facility: <strong className="text-text">{request?.hospital_name || 'Hospital Trauma Desk'}</strong> • City: <strong className="text-text">{request?.city}</strong> • Requirement: <strong className="text-text">{request?.units_required} Units</strong> ({request?.units_fulfilled} fulfilled)
              </p>
            </div>

            {/* Matching Control Actions */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 bg-surface/60 p-3 rounded-xl border border-border/80">
              <div className="flex items-center gap-2">
                <label className="text-xs font-semibold text-text-muted whitespace-nowrap">
                  Search Radius:
                </label>
                <select
                  value={searchRadius}
                  onChange={(e) => handleReRunMatching(parseFloat(e.target.value))}
                  disabled={isMatchingRunning}
                  className="bg-card border border-border rounded-lg text-xs font-medium px-2 py-1.5 text-text focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value={15}>15 km (Local)</option>
                  <option value={25}>25 km (District)</option>
                  <option value={50}>50 km (Regional)</option>
                  <option value={100}>100 km (Intercity)</option>
                </select>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleReRunMatching(searchRadius)}
                isLoading={isMatchingRunning}
              >
                🔄 Re-run AI Matching
              </Button>
            </div>
          </div>

          {/* Telemetry metadata footer */}
          {matchRun && (
            <div className="mt-4 pt-4 border-t border-border flex flex-wrap items-center justify-between text-xs text-text-muted gap-2">
              <div className="flex items-center gap-4">
                <span>Algorithm: <strong className="text-text">{matchRun.algorithm}</strong></span>
                <span>Model: <strong className="text-text">{matchRun.model_version}</strong></span>
                <span>Candidates Evaluated: <strong className="text-text">{matchRun.candidates_evaluated}</strong></span>
              </div>
              {matchRun.execution_duration_ms && (
                <span>Execution Time: <strong className="text-primary">{matchRun.execution_duration_ms} ms</strong></span>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI & Medical Safety Disclosure */}
      <div className="p-4 bg-info/10 border border-info/30 rounded-xl text-xs text-text-muted flex items-start gap-3">
        <span className="text-info text-base">🛡️</span>
        <div>
          <span className="font-semibold text-text">AI-Assisted Candidate Prioritization: </span>
          <span>
            Candidate ranking combines response propensity models, proximity decay, and stock availability. 
            <strong className="text-text"> Deterministic immunohematology compatibility (ABO/Rh rules) and clinical cooldown periods are strictly enforced as mandatory gates before AI scoring.</strong>
          </span>
        </div>
      </div>

      {/* Zero Candidates Empty State */}
      {!isMatchingRunning && totalCandidates === 0 && (
        <Card className="border-border p-10 text-center">
          <div className="max-w-md mx-auto space-y-4">
            <div className="w-16 h-16 mx-auto bg-warning/10 text-warning rounded-full flex items-center justify-center text-2xl font-bold">
              🔍
            </div>
            <h3 className="text-lg font-bold text-text">No Compatible Sources Found Within {searchRadius} km</h3>
            <p className="text-sm text-text-muted">
              There are currently no verified blood banks with unreserved {request?.blood_type} units or eligible voluntary donors within the chosen radius.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleReRunMatching(100.0)}
              >
                Expand Search to 100 km
              </Button>
              <Link href="/hospital/requests">
                <Button variant="outline" size="sm">
                  Return to Requests
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      )}

      {/* Candidate Recommendation Sections */}
      {totalCandidates > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Blood Banks Column */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">🏥</span>
                <h2 className="text-lg font-bold text-text">Verified Blood Banks</h2>
                <Badge variant="info" size="sm">{bloodBanks.length}</Badge>
              </div>
              <span className="text-xs text-text-muted">Ranked by stock & proximity</span>
            </div>

            {bloodBanks.length === 0 ? (
              <div className="p-6 rounded-xl border border-border/80 bg-card text-center text-sm text-text-muted">
                No blood banks with compatible unreserved stock found in {searchRadius} km.
              </div>
            ) : (
              bloodBanks.map((bb) => (
                <Card
                  key={bb.id}
                  className={`border-border transition-all ${
                    bb.status === 'SHORTLISTED'
                      ? 'ring-2 ring-success/50 bg-success/5'
                      : bb.status === 'DISMISSED'
                      ? 'opacity-60 bg-surface/30'
                      : 'hover:border-primary/40'
                  }`}
                >
                  <CardContent className="p-5 space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">
                            #{bb.rank}
                          </span>
                          <h3 className="font-bold text-text text-base">{bb.name}</h3>
                        </div>
                        <p className="text-xs text-text-muted">
                          📍 {bb.location_display}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <Badge variant="success" size="sm">
                          {bb.units_available} Units Available
                        </Badge>
                        <Badge variant="outline" size="sm">
                          {bb.compatibility_status}
                        </Badge>
                      </div>
                    </div>

                    {/* Explainability Bullets */}
                    <div className="bg-surface/50 p-3 rounded-lg border border-border/60 space-y-1 text-xs text-text-muted">
                      <span className="font-semibold text-text block mb-1">Recommendation Audit:</span>
                      {bb.explanation.map((exp, idx) => (
                        <div key={idx} className="flex items-start gap-1.5">
                          <span className="text-success font-bold">✓</span>
                          <span>{exp}</span>
                        </div>
                      ))}
                    </div>

                    {/* Operational Action Controls */}
                    <div className="flex items-center justify-between pt-2 border-t border-border/60">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-text-muted">
                          Status: <strong className="text-text">{bb.status}</strong>
                        </span>
                        {bb.blood_bank_response_status && (
                          <Badge
                            variant={
                              bb.blood_bank_response_status === 'ACCEPTED' || bb.blood_bank_response_status === 'PARTIALLY_ACCEPTED'
                                ? 'success'
                                : 'critical'
                            }
                            className="text-[10px] font-bold"
                          >
                            {bb.blood_bank_response_status === 'ACCEPTED'
                              ? `✓ Stock Committed (${bb.units_committed || bb.units_available}u)`
                              : bb.blood_bank_response_status === 'PARTIALLY_ACCEPTED'
                              ? `✓ Partial Commit (${bb.units_committed}u)`
                              : '✕ Declined'}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        {bb.status !== 'SHORTLISTED' && (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => handleCandidateStatusUpdate(bb.id, 'SHORTLISTED')}
                          >
                            ⭐ Shortlist
                          </Button>
                        )}
                        {bb.status !== 'DISMISSED' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCandidateStatusUpdate(bb.id, 'DISMISSED')}
                          >
                            Dismiss
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Voluntary Donors Column */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">🩸</span>
                <h2 className="text-lg font-bold text-text">Eligible Voluntary Donors</h2>
                <Badge variant="info" size="sm">{donors.length}</Badge>
              </div>
              <span className="text-xs text-text-muted">Zero-PII Privacy Safe</span>
            </div>

            {donors.length === 0 ? (
              <div className="p-6 rounded-xl border border-border/80 bg-card text-center text-sm text-text-muted">
                No eligible voluntary donors available within {searchRadius} km.
              </div>
            ) : (
              donors.map((donor) => {
                const aiPropensityPct = donor.ai_score ? Math.round(donor.ai_score * 100) : null;
                return (
                  <Card
                    key={donor.id}
                    className={`border-border transition-all ${
                      donor.status === 'SHORTLISTED'
                        ? 'ring-2 ring-success/50 bg-success/5'
                        : donor.status === 'DISMISSED'
                        ? 'opacity-60 bg-surface/30'
                        : 'hover:border-primary/40'
                    }`}
                  >
                    <CardContent className="p-5 space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">
                              #{donor.rank}
                            </span>
                            <h3 className="font-bold text-text text-base">{donor.name}</h3>
                            <Badge variant="outline" size="sm">
                              {donor.blood_type}
                            </Badge>
                          </div>
                          <p className="text-xs text-text-muted">
                            📍 {donor.location_display}
                          </p>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          {aiPropensityPct !== null ? (
                            <Badge
                              variant={aiPropensityPct >= 60 ? 'success' : aiPropensityPct >= 40 ? 'info' : 'default'}
                              size="sm"
                            >
                              AI Response Propensity: {aiPropensityPct}%
                            </Badge>
                          ) : (
                            <Badge variant="default" size="sm">
                              Deterministic Rank
                            </Badge>
                          )}
                          <span className="text-[10px] text-text-muted">
                            Composite Score: {Math.round(donor.total_score * 100)}/100
                          </span>
                        </div>
                      </div>

                      {/* Explainability Bullets */}
                      <div className="bg-surface/50 p-3 rounded-lg border border-border/60 space-y-1 text-xs text-text-muted">
                        <span className="font-semibold text-text block mb-1">Recommendation Audit:</span>
                        {donor.explanation.map((exp, idx) => (
                          <div key={idx} className="flex items-start gap-1.5">
                            <span className="text-success font-bold">✓</span>
                            <span>{exp}</span>
                          </div>
                        ))}
                      </div>

                      {/* Operational Action Controls */}
                      <div className="flex items-center justify-between pt-2 border-t border-border/60">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-text-muted">
                            Triage: <strong className="text-text">{donor.status}</strong>
                          </span>
                          {donor.donor_response_status && (
                            <Badge
                              variant={
                                donor.donor_response_status === 'ACCEPTED'
                                  ? 'success'
                                  : donor.donor_response_status === 'DECLINED'
                                  ? 'critical'
                                  : 'outline'
                              }
                              className="text-[10px] font-bold"
                            >
                              Donor: {donor.donor_response_status === 'ACCEPTED' ? '✓ Accepted' : donor.donor_response_status === 'DECLINED' ? '✕ Declined' : 'Pending Response'}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {donor.status !== 'SHORTLISTED' && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleCandidateStatusUpdate(donor.id, 'SHORTLISTED')}
                            >
                              ⭐ Shortlist
                            </Button>
                          )}
                          {donor.status !== 'DISMISSED' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCandidateStatusUpdate(donor.id, 'DISMISSED')}
                            >
                              Dismiss
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
