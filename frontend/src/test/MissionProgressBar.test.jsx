import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MissionProgressBar from '@/components/shared/MissionProgressBar'

describe('MissionProgressBar', () => {
  it('shows "Completed" badge when day_completed_id is set', () => {
    render(
      <MissionProgressBar
        mission={{ progress: 3, max_progress: 3, day_completed_id: 42 }}
      />
    )
    expect(screen.getByText('Completed')).toBeInTheDocument()
  })

  it('shows "In progress" for pass/fail mission with no progress', () => {
    render(
      <MissionProgressBar
        mission={{ progress: 0, max_progress: 0, day_completed_id: null }}
      />
    )
    expect(screen.getByText('In progress')).toBeInTheDocument()
  })

  it('shows "Pass" for pass/fail mission with progress > 0', () => {
    render(
      <MissionProgressBar
        mission={{ progress: 1, max_progress: 0, day_completed_id: null }}
      />
    )
    expect(screen.getByText('Pass')).toBeInTheDocument()
  })

  it('shows n/max label for multi-step mission', () => {
    render(
      <MissionProgressBar
        mission={{ progress: 2, max_progress: 3, day_completed_id: null }}
      />
    )
    expect(screen.getByText('2/3')).toBeInTheDocument()
  })

  it('shows 0/max when no progress yet', () => {
    render(
      <MissionProgressBar
        mission={{ progress: 0, max_progress: 2, day_completed_id: null }}
      />
    )
    expect(screen.getByText('0/2')).toBeInTheDocument()
  })
})
