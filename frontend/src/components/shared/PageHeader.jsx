import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function PageHeader({ title, backTo }) {
  const navigate = useNavigate()
  return (
    <div className="flex items-center gap-3 mb-6">
      {backTo && (
        <Button variant="ghost" size="icon" onClick={() => navigate(backTo)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
      )}
      <h1 className="text-2xl font-bold">{title}</h1>
    </div>
  )
}
