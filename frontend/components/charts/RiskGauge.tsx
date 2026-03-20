'use client';

import { useEffect, useRef } from 'react';

interface RiskGaugeProps {
  score: number;
  level: string;
  size?: number;
}

export function RiskGauge({ score, level, size = 200 }: RiskGaugeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = size / 2;
    const centerY = size / 2;
    const radius = size / 2 - 20;

    ctx.clearRect(0, 0, size, size);

    const gradient = ctx.createLinearGradient(0, 0, size, size);
    if (level === 'LOW') {
      gradient.addColorStop(0, '#10b981');
      gradient.addColorStop(1, '#059669');
    } else if (level === 'MEDIUM') {
      gradient.addColorStop(0, '#f59e0b');
      gradient.addColorStop(1, '#d97706');
    } else {
      gradient.addColorStop(0, '#ef4444');
      gradient.addColorStop(1, '#dc2626');
    }

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 15;
    ctx.stroke();

    const endAngle = Math.PI + (score * Math.PI);
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 15;
    ctx.lineCap = 'round';
    ctx.stroke();

    ctx.fillStyle = '#1f2937';
    ctx.font = `bold ${size / 8}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(`${(score * 100).toFixed(0)}%`, centerX, centerY - 10);

    ctx.font = `${size / 15}px sans-serif`;
    ctx.fillStyle = '#6b7280';
    ctx.fillText(level, centerX, centerY + 20);
  }, [score, level, size]);

  return (
    <div className="flex justify-center">
      <canvas ref={canvasRef} width={size} height={size} />
    </div>
  );
}
