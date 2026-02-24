import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

export default function MissionProgressBar({ mission }) {
  const { progress, max_progress, day_completed_id } = mission

  if (day_completed_id) {
    return <Badge variant="secondary">Completed</Badge>
  }

  if (max_progress === 0) {
    return (
      <div className="flex items-center gap-2">
        <Progress value={progress > 0 ? 100 : 0} className="h-2 flex-1" />
        <span className="text-xs text-muted-foreground">{progress > 0 ? 'Pass' : 'In progress'}</span>
      </div>
    )
  }

  const pct = Math.round((progress / max_progress) * 100)
  return (
    <div className="flex items-center gap-2">
      <Progress value={pct} className="h-2 flex-1" />
      <span className="text-xs text-muted-foreground">{progress}/{max_progress}</span>
    </div>
  )
}
