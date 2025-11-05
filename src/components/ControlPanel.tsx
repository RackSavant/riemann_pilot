import { SteeringDial } from './SteeringDial';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RotateCcw } from 'lucide-react';

interface SteeringVectors {
  love: number;
  theoryOfMind: number;
  eutopia: number;
  creativity: number;
}

interface ControlPanelProps {
  vectors: SteeringVectors;
  onVectorChange: (vector: keyof SteeringVectors, value: number) => void;
  featureAblation: string;
  onFeatureAblationChange: (value: string) => void;
  onReset: () => void;
}

export const ControlPanel = ({
  vectors,
  onVectorChange,
  featureAblation,
  onFeatureAblationChange,
  onReset,
}: ControlPanelProps) => {
  return (
    <Card className="p-4 border shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-foreground">
          Controls
        </h2>
        <Button
          variant="outline"
          size="sm"
          onClick={onReset}
          className="gap-1.5 text-xs"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="space-y-4 mb-4">
        <SteeringDial
          label="Love"
          value={vectors.love}
          onChange={(val) => onVectorChange('love', val)}
          color="love"
        />
        <SteeringDial
          label="Theory of Mind"
          value={vectors.theoryOfMind}
          onChange={(val) => onVectorChange('theoryOfMind', val)}
          color="theory"
        />
        <SteeringDial
          label="Eutopia"
          value={vectors.eutopia}
          onChange={(val) => onVectorChange('eutopia', val)}
          color="eutopia"
        />
        <SteeringDial
          label="Creativity"
          value={vectors.creativity}
          onChange={(val) => onVectorChange('creativity', val)}
          color="creativity"
        />
      </div>

      <div className="space-y-2 pt-4 border-t">
        <label className="text-sm font-medium">Feature Ablation</label>
        <Select value={featureAblation} onValueChange={onFeatureAblationChange}>
          <SelectTrigger className="text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="attention">Attention Layers</SelectItem>
            <SelectItem value="feedforward">Feed-Forward Layers</SelectItem>
            <SelectItem value="early">Early Layers (0-6)</SelectItem>
            <SelectItem value="middle">Middle Layers (7-18)</SelectItem>
            <SelectItem value="late">Late Layers (19-32)</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </Card>
  );
};
