/**
 * Component for generating animations
 * Provides a form for entering prompts and displays animation status
 */

import { useState, useEffect } from 'react';
import { useAnimation } from '@/hooks/use-animation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Loader2, Play, AlertCircle } from 'lucide-react';

interface AnimationGeneratorProps {
    onAnimationComplete?: (animationId: string) => void;
}

type ComponentStatus = 'idle' | 'generating' | 'completed' | 'error';

export function AnimationGenerator({ onAnimationComplete }: AnimationGeneratorProps) {
    const [prompt, setPrompt] = useState('');
    const [quality, setQuality] = useState('medium');
    const [currentAnimationId, setCurrentAnimationId] = useState<string | null>(null);
    const [status, setStatus] = useState<ComponentStatus>('idle');
    const [error, setError] = useState<string | null>(null);

    const { generateAnimation, checkStatus, loading } = useAnimation();

    // Map animation status to component status
    const mapAnimationStatus = (animationStatus: string): ComponentStatus => {
        switch (animationStatus) {
            case 'pending':
            case 'generating':
                return 'generating';
            case 'completed':
                return 'completed';
            case 'error':
                return 'error';
            default:
                return 'idle';
        }
    };

    // Poll for animation status when generating
    useEffect(() => {
        let intervalId: NodeJS.Timeout;

        const pollStatus = async () => {
            if (!currentAnimationId || status !== 'generating') return;

            try {
                const animation = await checkStatus(currentAnimationId);
                const newStatus = mapAnimationStatus(animation.status);
                setStatus(newStatus);

                if (newStatus === 'completed') {
                    onAnimationComplete?.(currentAnimationId);
                    setCurrentAnimationId(null);
                } else if (newStatus === 'error') {
                    setError(animation.error || 'Animation generation failed');
                    setCurrentAnimationId(null);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to check animation status');
                setStatus('error');
                setCurrentAnimationId(null);
            }
        };

        if (status === 'generating') {
            intervalId = setInterval(pollStatus, 2000); // Poll every 2 seconds
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [currentAnimationId, status, checkStatus, onAnimationComplete]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        setError(null);
        setStatus('generating');

        try {
            const animationId = await generateAnimation(prompt, quality);
            setCurrentAnimationId(animationId);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate animation');
            setStatus('error');
        }
    };

    return (
        <Card className="p-6 bg-slate-900/50 border border-slate-700/50 backdrop-blur-sm">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="prompt" className="text-blue-300 font-medium">
                        Animation Prompt
                    </Label>
                    <Input
                        id="prompt"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the animation you want to create..."
                        className="input-enhanced h-12 rounded-xl"
                        disabled={status === 'generating'}
                        required
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="quality" className="text-blue-300 font-medium">
                        Quality
                    </Label>
                    <Select
                        value={quality}
                        onValueChange={setQuality}
                        disabled={status === 'generating'}
                    >
                        <SelectTrigger className="h-12 rounded-xl">
                            <SelectValue placeholder="Select quality" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="low">Low (Faster)</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="high">High (Slower)</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {error && (
                    <div className="flex items-center gap-2 text-red-400 bg-red-500/10 border border-red-500/30 px-4 py-3 rounded-xl text-sm">
                        <AlertCircle className="w-5 h-5" />
                        <span>{error}</span>
                    </div>
                )}

                <Button
                    type="submit"
                    disabled={loading || status === 'generating' || !prompt.trim()}
                    className="w-full btn-primary h-12 rounded-xl text-base font-semibold"
                >
                    {status === 'generating' ? (
                        <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            Generating Animation...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5 mr-2" />
                            Generate Animation
                        </>
                    )}
                </Button>
            </form>

            {status === 'generating' && (
                <div className="mt-4 text-sm text-slate-400">
                    This may take a few minutes. You can close this window and check the status later.
                </div>
            )}
        </Card>
    );
} 