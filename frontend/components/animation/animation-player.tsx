/**
 * Component for displaying and playing animations
 * Handles video playback and controls
 */

import { useState, useEffect } from 'react';
import { useAnimation } from '@/hooks/use-animation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Play, Pause, Volume2, VolumeX, Maximize2 } from 'lucide-react';

interface AnimationPlayerProps {
    animationId: string;
    onClose?: () => void;
}

export function AnimationPlayer({ animationId, onClose }: AnimationPlayerProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const { getAnimation, loading } = useAnimation();

    useEffect(() => {
        const loadAnimation = async () => {
            try {
                const animation = await getAnimation(animationId);
                if (animation.status === 'completed' && animation.video_path) {
                    setVideoUrl(`http://localhost:5000${animation.video_path}`);
                } else if (animation.status === 'error') {
                    setError(animation.error || 'Animation generation failed');
                } else {
                    setError('Animation is not ready yet');
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load animation');
            }
        };

        loadAnimation();
    }, [animationId, getAnimation]);

    const handleFullscreen = () => {
        const videoElement = document.querySelector('video');
        if (!videoElement) return;

        if (!isFullscreen) {
            if (videoElement.requestFullscreen) {
                videoElement.requestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    };

    useEffect(() => {
        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };

        document.addEventListener('fullscreenchange', handleFullscreenChange);
        return () => {
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
        };
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        );
    }

    if (error) {
        return (
            <Card className="p-6 bg-red-500/10 border border-red-500/30">
                <div className="text-red-400 text-center">
                    <p className="font-medium mb-2">Error Loading Animation</p>
                    <p className="text-sm">{error}</p>
                </div>
            </Card>
        );
    }

    if (!videoUrl) {
        return (
            <Card className="p-6 bg-slate-900/50 border border-slate-700/50">
                <div className="text-slate-400 text-center">
                    <p>No video available</p>
                </div>
            </Card>
        );
    }

    return (
        <Card className="overflow-hidden bg-slate-900/50 border border-slate-700/50 backdrop-blur-sm">
            <div className="relative aspect-video bg-black">
                <video
                    src={videoUrl}
                    className="w-full h-full"
                    controls={false}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    muted={isMuted}
                />
                <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => {
                                    const video = document.querySelector('video');
                                    if (video) {
                                        if (isPlaying) {
                                            video.pause();
                                        } else {
                                            video.play();
                                        }
                                    }
                                }}
                                className="text-white hover:text-blue-400 hover:bg-white/10"
                            >
                                {isPlaying ? (
                                    <Pause className="w-5 h-5" />
                                ) : (
                                    <Play className="w-5 h-5" />
                                )}
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setIsMuted(!isMuted)}
                                className="text-white hover:text-blue-400 hover:bg-white/10"
                            >
                                {isMuted ? (
                                    <VolumeX className="w-5 h-5" />
                                ) : (
                                    <Volume2 className="w-5 h-5" />
                                )}
                            </Button>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleFullscreen}
                            className="text-white hover:text-blue-400 hover:bg-white/10"
                        >
                            <Maximize2 className="w-5 h-5" />
                        </Button>
                    </div>
                </div>
            </div>
        </Card>
    );
} 