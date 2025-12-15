import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '../../lib/api';
import { EngagementMetrics, FinancialMetrics } from '../../types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { useToast } from '../ui/Toast';
import { BarChart3, DollarSign } from 'lucide-react';

interface MetricsFormProps {
  startupId: string;
}

export function MetricsForm({ startupId }: MetricsFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const { register: registerEng, handleSubmit: handleSubmitEng, reset: resetEng } = useForm<EngagementMetrics>();
  const { register: registerFin, handleSubmit: handleSubmitFin, reset: resetFin } = useForm<FinancialMetrics>();

  const onEngagementSubmit = async (data: EngagementMetrics) => {
    setLoading(true);
    try {
      // Convert strings to numbers
      const payload: EngagementMetrics = Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, Number(v)])
      );
      await api.submitEngagementMetrics(startupId, payload);
      toast({ type: 'success', title: 'Metrics Updated', message: 'Engagement metrics saved successfully.' });
      resetEng();
    } catch (error) {
      toast({ type: 'error', title: 'Error', message: 'Failed to save engagement metrics.' });
    } finally {
      setLoading(false);
    }
  };

  const onFinancialSubmit = async (data: FinancialMetrics) => {
    setLoading(true);
    try {
      const payload: FinancialMetrics = Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, Number(v)])
      );
      await api.submitFinancialMetrics(startupId, payload);
      toast({ type: 'success', title: 'Metrics Updated', message: 'Financial metrics saved successfully.' });
      resetFin();
    } catch (error) {
      toast({ type: 'error', title: 'Error', message: 'Failed to save financial metrics.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Engagement Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Engagement Metrics
          </CardTitle>
          <CardDescription>Track user activity and retention.</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmitEng(onEngagementSubmit)}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="DAU (Daily Active)" type="number" {...registerEng('dau')} />
              <Input label="WAU (Weekly Active)" type="number" {...registerEng('wau')} />
            </div>
            <Input label="MAU (Monthly Active)" type="number" {...registerEng('mau')} />
            <div className="grid grid-cols-3 gap-2">
              <Input label="D1 Ret (%)" type="number" step="0.1" {...registerEng('retention_d1')} />
              <Input label="D7 Ret (%)" type="number" step="0.1" {...registerEng('retention_d7')} />
              <Input label="D30 Ret (%)" type="number" step="0.1" {...registerEng('retention_d30')} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="NPS Score" type="number" {...registerEng('nps_score')} />
              <Input label="Churn Rate (%)" type="number" step="0.01" {...registerEng('churn_rate')} />
            </div>
            <Button type="submit" className="w-full mt-4" isLoading={loading}>Update Engagement</Button>
          </CardContent>
        </form>
      </Card>

      {/* Financial Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            Financial Metrics
          </CardTitle>
          <CardDescription>Update your key financial health indicators.</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmitFin(onFinancialSubmit)}>
          <CardContent className="space-y-4">
            <Input label="MRR ($)" type="number" {...registerFin('mrr')} />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Burn Rate ($)" type="number" {...registerFin('burn_rate')} />
              <Input label="Runway (Months)" type="number" step="0.1" {...registerFin('runway_months')} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="LTV ($)" type="number" {...registerFin('ltv')} />
              <Input label="CAC ($)" type="number" {...registerFin('cac')} />
            </div>
            <Button type="submit" className="w-full mt-4" variant="secondary" isLoading={loading}>Update Financials</Button>
          </CardContent>
        </form>
      </Card>
    </div>
  );
}
