'use client';

// frontend/app/(dashboard)/blood-bank/page.tsx
// LifeLink AI — Blood Bank Operational Console with Real PostgreSQL Inventory
// Architecture Reference: ARCHITECTURE.md Section 15, 24, 27; DATABASE.md Section 8, 9

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { bloodBankService } from '@/services/bloodBankService';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import type {
  BloodBank,
  BloodBankDashboardData,
  BloodInventoryItem,
  DemandAvailabilityResult,
  InventorySummary,
} from '@/types';

export default function BloodBankDashboardPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [dashboard, setDashboard] = useState<BloodBankDashboardData | null>(null);
  const [inventoryItems, setInventoryItems] = useState<BloodInventoryItem[]>([]);
  const [inventorySummary, setInventorySummary] = useState<InventorySummary | null>(null);
  const [availabilities, setAvailabilities] = useState<Record<string, DemandAvailabilityResult>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Edit stock modal state
  const [editingItem, setEditingItem] = useState<BloodInventoryItem | null>(null);
  const [editUnits, setEditUnits] = useState<number>(0);
  const [editThreshold, setEditThreshold] = useState<number>(5);
  const [editExpiry, setEditExpiry] = useState<string>('');
  const [editReason, setEditReason] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);

  // Respond to Emergency modal state
  const [respondingReq, setRespondingReq] = useState<import('@/types').EmergencyDemandItem | null>(null);
  const [commitUnits, setCommitUnits] = useState<number>(1);
  const [commitMessage, setCommitMessage] = useState<string>('');
  const [isResponding, setIsResponding] = useState(false);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Fetch dashboard metrics & emergency demand
      const dashData = await bloodBankService.getDashboard();
      setDashboard(dashData);

      // 2. Fetch real PostgreSQL blood inventory
      const invData = await bloodBankService.getMyInventory();
      setInventoryItems(invData.items);
      setInventorySummary(invData.summary);

      // 3. For each active emergency demand request, fetch availability asynchronously
      if (dashData.emergency_demand && dashData.emergency_demand.length > 0) {
        const availMap: Record<string, DemandAvailabilityResult> = {};
        await Promise.all(
          dashData.emergency_demand.map(async (req) => {
            try {
              const res = await bloodBankService.checkDemandAvailability(req.id);
              availMap[req.id] = res;
            } catch (e) {
              // Ignore single request availability errors
            }
          })
        );
        setAvailabilities(availMap);
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        router.push('/blood-bank/profile');
        return;
      }
      setError(err.response?.data?.error?.message || 'Failed to load blood bank operational console.');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, loadData]);

  const openRespondModal = (req: import('@/types').EmergencyDemandItem) => {
    setRespondingReq(req);
    const avail = availabilities[req.id];
    const maxUnits = avail ? Math.min(avail.total_compatible_units, req.units_required) : req.units_required;
    setCommitUnits(maxUnits > 0 ? maxUnits : 1);
    setCommitMessage('');
  };

  const handleCommitStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!respondingReq) return;

    setIsResponding(true);
    setError(null);
    try {
      await bloodBankService.respondToEmergency(respondingReq.id, {
        units_committed: Number(commitUnits),
        blood_type: respondingReq.blood_type,
        status: 'ACCEPTED',
        message: commitMessage || 'Committed from cold storage by blood bank operations',
      });
      setSuccessMsg(`Successfully committed and reserved ${commitUnits} units for request #${respondingReq.request_number}`);
      setRespondingReq(null);
      await loadData();
      setTimeout(() => setSuccessMsg(null), 5000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.message || 'Failed to commit stock for emergency.');
    } finally {
      setIsResponding(false);
    }
  };

  const openEditModal = (item: BloodInventoryItem) => {
    setEditingItem(item);
    setEditUnits(item.units_available);
    setEditThreshold(item.minimum_threshold);
    setEditExpiry(item.expiry_date || '');
    setEditReason('');
  };

  const handleSaveStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingItem) return;

    setIsUpdating(true);
    setError(null);
    try {
      await bloodBankService.updateInventoryItem(editingItem.blood_type, {
        units_available: Number(editUnits),
        minimum_threshold: Number(editThreshold),
        expiry_date: editExpiry || null,
        reason: editReason || 'Manual stock update',
      });
      setSuccessMsg(`Successfully updated stock for blood type ${editingItem.blood_type}`);
      setEditingItem(null);
      await loadData();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to update blood stock.');
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm font-medium">Connecting to Blood Bank Cold Chain Storage...</p>
        </div>
      </div>
    );
  }

  const bank = dashboard?.blood_bank;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              {bank?.name || 'Blood Bank Operations Console'}
            </h1>
            {bank?.is_verified ? (
              <Badge variant="success" size="sm">Licensed Facility</Badge>
            ) : (
              <Badge variant="warning" size="sm">Verification Pending</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {bank?.city}, {bank?.state} &bull; License: <span className="font-semibold">{bank?.license_number || 'Pending Reg'}</span>
            {bank?.is_24_hours && ' &bull; 24/7 Round the Clock Service'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/blood-bank/profile">
            <Button variant="outline" size="sm">
              ⚙️ Facility Settings
            </Button>
          </Link>
          <Button
            variant="secondary"
            size="sm"
            onClick={loadData}
          >
            🔄 Refresh Storage &amp; Demand
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-critical/30 bg-critical-subtle text-critical text-sm">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl border border-success/30 bg-success-subtle text-success text-sm">
          {successMsg}
        </div>
      )}

      {/* KPI Cards — Cold Storage & Emergency Operations */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Available Units */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">
              Available Units
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-primary">
              {inventorySummary?.total_available ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Physically verified non-expired blood units in cold storage
            </p>
          </CardContent>
        </Card>

        {/* Card 2: Expiring Soon Alert */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">
              Expiring Soon
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-warning">
              {inventorySummary?.expiring_soon_count ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Units expiring within 7 days requiring prioritized rotation
            </p>
          </CardContent>
        </Card>

        {/* Card 3: Stockout Depleted Groups */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">
              Stockout Risk
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-critical">
              {inventorySummary?.depleted_groups_count ?? 0} <span className="text-sm font-normal text-muted-foreground">/ 8</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Blood groups at zero or below safety threshold
            </p>
          </CardContent>
        </Card>

        {/* Card 4: Regional Emergency Demand */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">
              Emergency Demand
            </CardDescription>
            <CardTitle className="text-3xl font-extrabold text-info">
              {dashboard?.active_emergency_demand_count ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Active requisitions in {bank?.city || 'your jurisdiction'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Real PostgreSQL Blood Inventory Management */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
              <span>❄️</span> Cold Chain Blood Storage (PostgreSQL Managed)
            </h2>
            <p className="text-xs text-muted-foreground">
              Live inventory tracking across all 8 ABO/Rh blood groups. Zero mock data — physical counts backed by audit ledger.
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Blood Group</th>
                  <th className="py-3 px-4">Component</th>
                  <th className="py-3 px-4">Available Units</th>
                  <th className="py-3 px-4">Reserved</th>
                  <th className="py-3 px-4">Buffer Threshold</th>
                  <th className="py-3 px-4">Earliest Expiry</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {inventoryItems.map((item) => (
                  <tr key={item.blood_type} className="hover:bg-muted/20 transition-colors">
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center justify-center font-extrabold text-sm px-2.5 py-1 rounded-lg bg-primary/10 text-primary border border-primary/20">
                        {item.blood_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-foreground">
                      {item.component.replace('_', ' ')}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-base text-foreground">
                      {item.is_expired ? (
                        <span className="text-critical line-through">{item.units_available} (Expired)</span>
                      ) : (
                        item.units_available
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-muted-foreground">
                      {item.units_reserved}
                    </td>
                    <td className="py-3.5 px-4 text-muted-foreground">
                      {item.minimum_threshold} units
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">
                      {item.expiry_date ? (
                        <span className={item.is_expired ? 'text-critical font-bold' : 'text-foreground'}>
                          {item.expiry_date}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">Not Recorded</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {item.is_expired ? (
                        <Badge variant="critical" size="sm">EXPIRED</Badge>
                      ) : item.units_available === 0 ? (
                        <Badge variant="outline" size="sm">OUT OF STOCK</Badge>
                      ) : item.is_low_stock ? (
                        <Badge variant="warning" size="sm">LOW BUFFER</Badge>
                      ) : (
                        <Badge variant="success" size="sm">AVAILABLE</Badge>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditModal(item)}
                      >
                        ✏️ Adjust Stock
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Regional Emergency Blood Demand Table with Live Compatibility & Availability Indicator */}
      <div className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
              <span>🚨</span> Regional Emergency Blood Demand &amp; Stock Availability
            </h2>
            <p className="text-xs text-muted-foreground">
              Emergency trauma requisitions in {bank?.city}. The availability indicator dynamically checks your real cold-chain stock against ABO/Rh compatibility rules.
            </p>
          </div>
        </div>

        {dashboard?.emergency_demand && dashboard.emergency_demand.length > 0 ? (
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Requisition ID</th>
                    <th className="py-3 px-4">Hospital Destination</th>
                    <th className="py-3 px-4">Blood Needed</th>
                    <th className="py-3 px-4">Units Required</th>
                    <th className="py-3 px-4">Urgency</th>
                    <th className="py-3 px-4">Your Compatible Availability</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {dashboard.emergency_demand.map((req) => {
                    const avail = availabilities[req.id];
                    return (
                      <tr key={req.id} className="hover:bg-muted/20 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-foreground">
                          {req.request_number}
                        </td>
                        <td className="py-3 px-4 font-medium text-foreground">
                          {req.hospital_name}
                        </td>
                        <td className="py-3 px-4">
                          <span className="inline-flex items-center justify-center font-bold px-2 py-0.5 rounded bg-primary/10 text-primary">
                            {req.blood_type}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-foreground">
                          {req.units_required} units
                        </td>
                        <td className="py-3 px-4">
                          <Badge
                            variant={
                              req.urgency_level === 'CRITICAL'
                                ? 'critical'
                                : req.urgency_level === 'HIGH'
                                ? 'warning'
                                : 'default'
                            }
                            size="sm"
                          >
                            {req.urgency_level}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          {avail ? (
                            <div className="space-y-1">
                              {avail.availability_status === 'AVAILABLE' ? (
                                <Badge variant="success" size="sm">
                                  🟢 Compatible Stock Available ({avail.total_compatible_units} units)
                                </Badge>
                              ) : avail.availability_status === 'PARTIAL' ? (
                                <Badge variant="warning" size="sm">
                                  🟡 Partial Compatible Stock ({avail.total_compatible_units} units)
                                </Badge>
                              ) : (
                                <Badge variant="critical" size="sm">
                                  🔴 Zero Compatible Stock
                                </Badge>
                              )}
                              {avail.compatible_breakdown && avail.compatible_breakdown.length > 0 && (
                                <p className="text-[11px] text-muted-foreground">
                                  Match: {avail.compatible_breakdown.map(b => `${b.blood_type}: ${b.units_available}u`).join(', ')}
                                </p>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-muted-foreground">Checking stock...</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {avail && avail.total_compatible_units > 0 && req.status !== 'FULFILLED' && req.status !== 'CANCELLED' && (
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => openRespondModal(req)}
                                className="text-xs font-semibold"
                              >
                                ⚡ Accept &amp; Commit Stock
                              </Button>
                            )}
                            <Link href={`/emergency/track/${req.id}`}>
                              <Button variant="outline" size="sm">
                                Track ↗
                              </Button>
                            </Link>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="py-12 text-center flex flex-col items-center justify-center gap-3">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center text-2xl">
                🩸
              </div>
              <div className="max-w-md">
                <h3 className="text-base font-semibold text-foreground">
                  No active emergency requisitions in your area
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  There are currently no unmet emergency blood requisitions in {bank?.city}. New trauma dispatches will automatically appear here with real-time stock compatibility analysis.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Stock Adjustment Modal */}
      {editingItem && (
        <Modal
          isOpen={true}
          onClose={() => setEditingItem(null)}
          title={`Adjust Cold Chain Stock — ${editingItem.blood_type}`}
        >
          <form onSubmit={handleSaveStock} className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Modify the physically verified blood unit quantity and shelf life in your cold-storage facility.
            </p>

            <Input
              label="Physical Units Available"
              type="number"
              min="0"
              value={editUnits}
              onChange={(e) => setEditUnits(parseInt(e.target.value) || 0)}
              required
              helperText="Exact count of verified blood bags currently in cold chain storage."
            />

            <Input
              label="Minimum Safe Buffer Threshold"
              type="number"
              min="0"
              value={editThreshold}
              onChange={(e) => setEditThreshold(parseInt(e.target.value) || 0)}
              required
              helperText="Alert threshold below which a low-stock notice is triggered."
            />

            <Input
              label="Earliest Batch Expiry Date"
              type="date"
              value={editExpiry}
              onChange={(e) => setEditExpiry(e.target.value)}
              helperText="Date after which units in this batch must be quarantined and cannot be transfused."
            />

            <Input
              label="Audit Change Reason"
              type="text"
              placeholder="e.g. Donation drive intake, physical inventory audit"
              value={editReason}
              onChange={(e) => setEditReason(e.target.value)}
              helperText="Recorded in the permanent immutable inventory history ledger."
            />

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setEditingItem(null)}
                disabled={isUpdating}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isUpdating}
              >
                Save Stock Changes
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Respond to Emergency Modal */}
      {respondingReq && (
        <Modal
          isOpen={true}
          onClose={() => setRespondingReq(null)}
          title={`Accept & Reserve Stock for #${respondingReq.request_number}`}
        >
          <form onSubmit={handleCommitStock} className="space-y-4">
            <div className="rounded-lg bg-primary/5 border border-primary/20 p-3 text-xs space-y-1">
              <div className="font-semibold text-foreground">
                Destination: {respondingReq.hospital_name} ({respondingReq.city})
              </div>
              <div className="text-muted-foreground">
                Required Blood Group: <span className="font-bold text-primary">{respondingReq.blood_type}</span> ({respondingReq.units_required} units needed)
              </div>
              {availabilities[respondingReq.id] && (
                <div className="text-green-600 dark:text-green-400 font-medium pt-1">
                  ✓ Compatible stock on hand: {availabilities[respondingReq.id].total_compatible_units} units available
                </div>
              )}
            </div>

            <Input
              label="Units to Commit & Reserve"
              type="number"
              min="1"
              max={availabilities[respondingReq.id]?.total_compatible_units || respondingReq.units_required}
              value={commitUnits}
              onChange={(e) => setCommitUnits(parseInt(e.target.value) || 1)}
              required
              helperText="These units will be immediately reserved from cold storage via row-level pessimistic locking."
            />

            <Input
              label="Dispatch & Coordination Message"
              type="text"
              placeholder="e.g. Cold chain dispatch ready. Courier ETA 20 mins."
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              helperText="Visible to trauma surgeons and hospital coordination staff."
            />

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setRespondingReq(null)}
                disabled={isResponding}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isResponding}
              >
                Confirm Stock Reservation
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
