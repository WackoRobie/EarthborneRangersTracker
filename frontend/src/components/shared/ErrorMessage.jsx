import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message }) {
  return (
    <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
      <AlertCircle className="h-4 w-4 shrink-0" />
      <p className="text-sm">{message}</p>
    </div>
  )
}
