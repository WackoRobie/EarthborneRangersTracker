import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ErrorMessage from '@/components/shared/ErrorMessage'

describe('ErrorMessage', () => {
  it('renders the provided message', () => {
    render(<ErrorMessage message="Something went wrong" />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders an icon alongside the message', () => {
    const { container } = render(<ErrorMessage message="Error!" />)
    // lucide renders an SVG
    expect(container.querySelector('svg')).not.toBeNull()
  })
})
