import React from 'react';
import { Link } from 'react-router-dom';
import { Startup, SignalScores } from '../../types';
import { Card, CardContent, CardFooter, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { Users, Briefcase, ArrowRight } from 'lucide-react';

interface StartupCardProps {
  startup: Startup;
  latestSignal?: SignalScores;
}

export const StartupCard: React.FC<StartupCardProps> = ({ startup, latestSignal }) => {
  const getStageVariant = (stage: string) => {
    switch(stage) {
      case 'idea': return 'secondary';
      case 'mvp': return 'warning';
      case 'growth': return 'default';
      case 'scale': return 'success';
      default: return 'outline';
    }
  };

  const score = latestSignal?.composite_score || 0;

  return (
    <Link to={`/startups/${startup.id}`}>
      <Card className="h-full hover:shadow-md transition-shadow cursor-pointer flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start">
            <h3 className="font-bold text-lg text-gray-900 truncate pr-2">{startup.name}</h3>
            <Badge variant={getStageVariant(startup.stage) as any} className="uppercase text-[10px]">
              {startup.stage}
            </Badge>
          </div>
          <p className="text-sm text-gray-500 line-clamp-2 min-h-[40px]">
            {startup.description || "No description provided."}
          </p>
        </CardHeader>
        
        <CardContent className="flex-1 space-y-4">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            {startup.industry && (
              <div className="flex items-center gap-1.5">
                <Briefcase className="w-4 h-4" />
                <span>{startup.industry}</span>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <Users className="w-4 h-4" />
              <span>{startup.team_size} members</span>
            </div>
          </div>
          
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="font-medium text-gray-600">Signal Score</span>
              <span className="font-bold text-gray-900">{score}/100</span>
            </div>
            <Progress value={score} className="h-1.5" />
          </div>
        </CardContent>

        <CardFooter className="pt-3 border-t bg-gray-50/50 rounded-b-xl">
          <div className="w-full flex items-center justify-between text-sm text-blue-600 font-medium group">
            <span>Manage Startup</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}