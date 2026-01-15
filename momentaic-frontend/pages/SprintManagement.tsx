import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { WeeklySprint, DailyStandup, StandupStatus } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { Badge } from '../components/ui/Badge';
import { Dialog } from '../components/ui/Dialog';
import { Plus, CheckCircle, Clock, Award } from 'lucide-react';
import { useForm } from 'react-hook-form';

interface SprintManagementProps {
    startupId: string;
}

export default function SprintManagement({ startupId }: SprintManagementProps) {
    const [currentSprint, setCurrentSprint] = useState<WeeklySprint | null>(null);
    const [todayStandup, setTodayStandup] = useState<StandupStatus | null>(null);
    const [isCreateSprintOpen, setCreateSprintOpen] = useState(false);
    const [activeStandupView, setActiveStandupView] = useState<'morning' | 'evening' | null>(null);
    const { register, handleSubmit, reset } = useForm();
    const [loading, setLoading] = useState(false);

    const loadData = async () => {
        const [sprint, standup] = await Promise.all([
            api.getCurrentSprint(startupId),
            api.getTodayStandup(startupId)
        ]);
        setCurrentSprint(sprint);
        setTodayStandup(standup);
    };

    useEffect(() => {
        loadData();
    }, [startupId]);

    const handleCreateSprint = async (data: any) => {
        setLoading(true);
        await api.createSprint(startupId, {
            weekly_goal: data.weekly_goal,
            key_metric_name: data.key_metric_name,
            key_metric_start: Number(data.key_metric_start)
        });
        await loadData();
        setLoading(false);
        setCreateSprintOpen(false);
        reset();
    };

    const handleMorningStandup = async (data: any) => {
        await api.submitMorningStandup(startupId, data.morning_goal);
        await loadData();
        setActiveStandupView(null);
    };

    const handleEveningStandup = async (data: any) => {
        await api.submitEveningStandup(startupId, {
            evening_result: data.evening_result,
            goal_completed: data.goal_completed === 'yes'
        });
        await loadData();
        setActiveStandupView(null);
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Sprint Section */}
                <div className="lg:col-span-2 space-y-6">
                    <Card className="bg-gradient-to-r from-blue-50 to-white border-blue-100">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <CardTitle className="text-blue-900">Current Weekly Sprint</CardTitle>
                                {currentSprint ? <Badge variant="success">Active</Badge> : <Badge variant="secondary">No Sprint</Badge>}
                            </div>
                        </CardHeader>
                        <CardContent>
                            {currentSprint ? (
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-sm font-medium text-blue-600 uppercase tracking-wide">Weekly Goal</h3>
                                        <p className="text-xl font-bold text-gray-900 mt-1">{currentSprint.weekly_goal}</p>
                                    </div>
                                    {currentSprint.key_metric_name && (
                                        <div className="bg-white p-4 rounded-lg border border-blue-100 shadow-sm inline-block">
                                            <div className="text-sm text-gray-500">{currentSprint.key_metric_name} Start</div>
                                            <div className="text-2xl font-bold text-blue-600">{currentSprint.key_metric_start}</div>
                                        </div>
                                    )}
                                    {currentSprint.momentum_ai_feedback && (
                                        <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100 text-sm text-yellow-800">
                                            <strong>Momentum AI Tip:</strong> {currentSprint.momentum_ai_feedback}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <p className="text-gray-500 mb-4">Start a new sprint to focus your team's efforts this week.</p>
                                    <Button onClick={() => setCreateSprintOpen(true)}>
                                        <Plus className="w-4 h-4 mr-2" /> Start Sprint
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Standup History (Placeholder list) */}
                    <h3 className="text-lg font-semibold">Recent Standups</h3>
                    <div className="space-y-3">
                         {/* Mock history items */}
                        <Card className="opacity-75">
                             <CardContent className="p-4 flex items-center justify-between">
                                 <div>
                                     <div className="font-medium text-gray-900">Yesterday</div>
                                     <div className="text-sm text-gray-500">Completed API Integration</div>
                                 </div>
                                 <CheckCircle className="text-green-500 w-5 h-5" />
                             </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Daily Actions */}
                <div className="space-y-6">
                     <Card className="border-l-4 border-l-blue-500">
                         <CardHeader>
                             <CardTitle className="text-lg">Daily Standup</CardTitle>
                             <CardDescription>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric'})}</CardDescription>
                         </CardHeader>
                         <CardContent className="space-y-4">
                             {/* Morning Status */}
                             <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                 <div className="flex items-center gap-3">
                                     <div className={`p-2 rounded-full ${todayStandup?.morning_submitted ? 'bg-green-100 text-green-600' : 'bg-gray-200 text-gray-500'}`}>
                                         <Clock className="w-4 h-4" />
                                     </div>
                                     <div>
                                         <div className="font-medium text-sm">Morning Check-in</div>
                                         <div className="text-xs text-gray-500">{todayStandup?.morning_submitted ? 'Completed' : 'Pending'}</div>
                                     </div>
                                 </div>
                                 {!todayStandup?.morning_submitted && (
                                     <Button size="sm" onClick={() => setActiveStandupView('morning')}>Start</Button>
                                 )}
                             </div>

                             {/* Evening Status */}
                             <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                 <div className="flex items-center gap-3">
                                     <div className={`p-2 rounded-full ${todayStandup?.evening_submitted ? 'bg-green-100 text-green-600' : 'bg-gray-200 text-gray-500'}`}>
                                         <Award className="w-4 h-4" />
                                     </div>
                                     <div>
                                         <div className="font-medium text-sm">Evening Review</div>
                                         <div className="text-xs text-gray-500">{todayStandup?.evening_submitted ? 'Completed' : 'Pending'}</div>
                                     </div>
                                 </div>
                                 {todayStandup?.morning_submitted && !todayStandup?.evening_submitted && (
                                     <Button size="sm" onClick={() => setActiveStandupView('evening')}>Start</Button>
                                 )}
                             </div>
                         </CardContent>
                     </Card>
                </div>
            </div>

            {/* Create Sprint Dialog */}
            <Dialog 
                isOpen={isCreateSprintOpen} 
                onClose={() => setCreateSprintOpen(false)}
                title="Start New Sprint"
            >
                <form onSubmit={handleSubmit(handleCreateSprint)} className="space-y-4">
                    <Input 
                        label="Weekly Goal" 
                        placeholder="What is the ONE thing that matters this week?"
                        {...register('weekly_goal', { required: true })}
                    />
                    <div className="grid grid-cols-2 gap-4">
                        <Input 
                            label="Key Metric Name (Optional)" 
                            placeholder="e.g. MRR, DAU"
                            {...register('key_metric_name')}
                        />
                         <Input 
                            label="Start Value" 
                            type="number"
                            placeholder="0"
                            {...register('key_metric_start')}
                        />
                    </div>
                    <div className="flex justify-end pt-4">
                        <Button type="submit" isLoading={loading}>Launch Sprint</Button>
                    </div>
                </form>
            </Dialog>

            {/* Morning Standup Dialog */}
            <Dialog
                isOpen={activeStandupView === 'morning'}
                onClose={() => setActiveStandupView(null)}
                title="Morning Standup"
            >
                <form onSubmit={handleSubmit(handleMorningStandup)} className="space-y-4">
                     <Textarea 
                        label="What will you achieve today?"
                        placeholder="List your top 3 priorities..."
                        {...register('morning_goal', { required: true })}
                     />
                     <Button type="submit" className="w-full">Commit to Goal</Button>
                </form>
            </Dialog>

             {/* Evening Standup Dialog */}
             <Dialog
                isOpen={activeStandupView === 'evening'}
                onClose={() => setActiveStandupView(null)}
                title="Evening Review"
            >
                <form onSubmit={handleSubmit(handleEveningStandup)} className="space-y-4">
                     <label className="block text-sm font-medium text-gray-700">Did you complete your daily goal?</label>
                     <select {...register('goal_completed')} className="w-full p-2 border rounded-md">
                         <option value="yes">Yes, I crushed it</option>
                         <option value="no">No, I got blocked</option>
                     </select>
                     
                     <Textarea 
                        label="What did you ship? Any blockers?"
                        placeholder="Describe your progress..."
                        {...register('evening_result', { required: true })}
                     />
                     <Button type="submit" className="w-full">Submit Review</Button>
                </form>
            </Dialog>
        </div>
    );
}