import { Slider } from '@/components/ui/slider';

interface SteeringDialProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  color: 'love' | 'theory' | 'eutopia' | 'creativity';
}

export const SteeringDial = ({ label, value, onChange, color }: SteeringDialProps) => {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <span 
          className="text-sm font-semibold tabular-nums"
          style={{ color: `hsl(var(--vector-${color}))` }}
        >
          {value}%
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        max={100}
        step={1}
        className="w-full"
      />
    </div>
  );
};
