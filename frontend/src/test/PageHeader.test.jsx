import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import PageHeader from '@/components/shared/PageHeader'

function renderWithRouter(ui) {
  return render(<MemoryRouter>{ui}</MemoryRouter>)
}

describe('PageHeader', () => {
  it('renders the title', () => {
    renderWithRouter(<PageHeader title="My Campaign" />)
    expect(screen.getByText('My Campaign')).toBeInTheDocument()
  })

  it('does not render a back button when backTo is not provided', () => {
    renderWithRouter(<PageHeader title="No Back" />)
    // The back button contains an ArrowLeft icon (svg); if absent, no button
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('renders a back button when backTo is provided', () => {
    renderWithRouter(<PageHeader title="With Back" backTo="/" />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
})
