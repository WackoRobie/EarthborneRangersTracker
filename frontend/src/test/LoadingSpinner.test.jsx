import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LoadingSpinner from '@/components/shared/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders without crashing', () => {
    const { container } = render(<LoadingSpinner />)
    expect(container.firstChild).not.toBeNull()
  })

  it('renders a spinner SVG icon', () => {
    const { container } = render(<LoadingSpinner />)
    expect(container.querySelector('svg')).not.toBeNull()
  })
})
