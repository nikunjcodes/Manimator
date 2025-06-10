/**
 * Component for displaying a list of animations
 * Shows animation status, creation date, and provides controls
 */

import { useEffect, useState } from 'react';
import { useAnimation } from '@/hooks/use-animation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Loader2, Play, Trash2, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AnimationListProps {
    onAnimationSelect?: (animationId: string) => void;
}

export function AnimationList({ onAnimationSelect }: AnimationListProps) {
    const [page, setPage] = useState(1);
    const { animations, loading, error, listAnimations, deleteAnimation } = useAnimation();
    const ITEMS_PER_PAGE = 5;

    useEffect(() => {
        listAnimations((page - 1) * ITEMS_PER_PAGE, ITEMS_PER_PAGE);
    }, [page, listAnimations]);

    const handleDelete = async (animationId: string) => {
        if (window.confirm('Are you sure you want to delete this animation?')) {
            try {
                await deleteAnimation(animationId);
                // Refresh the list
                listAnimations((page - 1) * ITEMS_PER_PAGE, ITEMS_PER_PAGE);
            } catch (err) {
                console.error('Failed to delete animation:', err);
            }
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle2 className="w-5 h-5 text-green-400" />;
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-400" />;
            case 'pending':
            case 'generating':
                return <Clock className="w-5 h-5 text-blue-400" />;
            default:
                return null;
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case 'completed':
                return 'Completed';
            case 'error':
                return 'Failed';
            case 'pending':
                return 'Pending';
            case 'generating':
                return 'Generating';
            default:
                return status;
        }
    };

    if (loading && animations.length === 0) {
        return (
            <div className="flex items-center justify-center p-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center gap-2 text-red-400 bg-red-500/10 border border-red-500/30 px-4 py-3 rounded-xl">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
            </div>
        );
    }

    if (animations.length === 0) {
        return (
            <div className="text-center p-8 text-slate-400">
                No animations yet. Create your first animation using the generator above!
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {animations.map((animation) => (
                <Card
                    key={animation._id}
                    className="p-4 bg-slate-900/50 border border-slate-700/50 backdrop-blur-sm hover:border-slate-600/50 transition-colors"
                >
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                                {getStatusIcon(animation.status)}
                                <span className="text-sm font-medium text-slate-300">
                                    {getStatusText(animation.status)}
                                </span>
                                <span className="text-sm text-slate-500">
                                    {formatDistanceToNow(new Date(animation.created_at), { addSuffix: true })}
                                </span>
                            </div>
                            <p className="text-slate-300 mb-2">{animation.prompt}</p>
                            {animation.error && (
                                <p className="text-sm text-red-400">{animation.error}</p>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            {animation.status === 'completed' && animation.video_path && (
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => onAnimationSelect?.(animation._id)}
                                    className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                                >
                                    <Play className="w-5 h-5" />
                                </Button>
                            )}
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDelete(animation._id)}
                                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                            >
                                <Trash2 className="w-5 h-5" />
                            </Button>
                        </div>
                    </div>
                </Card>
            ))}

            <div className="flex justify-center gap-2 mt-4">
                <Button
                    variant="outline"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1 || loading}
                    className="btn-secondary"
                >
                    Previous
                </Button>
                <Button
                    variant="outline"
                    onClick={() => setPage(p => p + 1)}
                    disabled={animations.length < ITEMS_PER_PAGE || loading}
                    className="btn-secondary"
                >
                    Next
                </Button>
            </div>
        </div>
    );
} 