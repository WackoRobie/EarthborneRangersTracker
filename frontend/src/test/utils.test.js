import { describe, it, expect } from 'vitest'
import { cn } from '@/lib/utils'

describe('cn()', () => {
  it('returns a single class unchanged', () => {
    expect(cn('foo')).toBe('foo')
  })

  it('joins multiple classes', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
  })

  it('ignores falsy values', () => {
    expect(cn('foo', undefined, null, false, 'bar')).toBe('foo bar')
  })

  it('merges conflicting Tailwind classes (last wins)', () => {
    // tailwind-merge should keep the later padding class
    expect(cn('p-4', 'p-8')).toBe('p-8')
  })

  it('supports conditional object syntax from clsx', () => {
    expect(cn({ 'text-red-500': true, 'text-blue-500': false })).toBe('text-red-500')
  })

  it('handles empty input', () => {
    expect(cn()).toBe('')
  })
})
